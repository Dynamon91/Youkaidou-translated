"""Exact bit-stream LZSS codec and bounded event-script localization."""
import hashlib
import re
import struct

SCRIPT_SOURCE = 0x70725F
SCRIPT_DEST = 0x790000
SCRIPT_SIZE = 6940
LOWERCASE_START = 0x320
PUNCTUATION = {' ':0, '!':1, '"':2, "'":0x3B, '(':7, ')':8, '*':9,
               '+':0xA, ',':0x1E, '-':0xD, '/':0xF, ':':0x1A,
               '=':0x1D, '?':0x1F, '.':0x20}
VARIABLES = {'PLAYER_NAME':0x1000}


def decode_lzss(data, offset=0, max_output=0x40000):
    if offset+4>len(data): raise ValueError('Truncated LZSS header')
    size = int.from_bytes(data[offset:offset+4], 'big')
    if not 0<size<=max_output: raise ValueError('Invalid decompressed size')
    bit = (offset+4)*8
    ring = bytearray(4096)
    cursor = 0xFEE
    out = bytearray()
    def read(count):
        nonlocal bit
        value=0
        for _ in range(count):
            if bit>=len(data)*8: raise ValueError('Truncated LZSS bit stream')
            value=(value<<1) | (data[bit//8]>>(7-bit%8)&1)
            bit+=1
        return value
    while len(out)<size:
        if read(1)==0:
            value=read(8)
            out.append(value);ring[cursor]=value;cursor=(cursor+1)&4095
        else:
            index=read(12);count=read(4)+3
            for n in range(count):
                value=ring[(index+n)&4095]
                out.append(value);ring[cursor]=value;cursor=(cursor+1)&4095
                if len(out)==size: break
    return bytes(out),(bit+7)//8


def encode_lzss_literals(data):
    """Emit the stock decoder's literal form without a dictionary dependency."""
    result=bytearray(len(data).to_bytes(4,'big'))
    pending=0;count=0
    for byte in data:
        # A zero tag and eight data bits are packed continuously, MSB first.
        pending=(pending<<9)|byte;count+=9
        while count>=8:
            count-=8;result.append((pending>>count)&255)
            pending &= (1<<count)-1
    if count: result.append(pending<<(8-count))
    return bytes(result)


def encode_story(text):
    if '\n' in text or '\r' in text:
        raise ValueError('Use separate script print slots for line breaks')
    words=[];cells=0;variables=[]
    for token in re.findall(r'\{[A-Z_]+\}|.',text):
        if token.startswith('{'):
            name=token[1:-1]
            if name not in VARIABLES: raise ValueError('Unknown variable '+token)
            words.append(VARIABLES[name]);cells+=8;variables.append(name)
        elif 'A'<=token<='Z':words.append(0x21+ord(token)-ord('A'));cells+=1
        elif 'a'<=token<='z':words.append(LOWERCASE_START+ord(token)-ord('a'));cells+=1
        elif '0'<=token<='9':words.append(0x10+ord(token)-ord('0'));cells+=1
        elif token in PUNCTUATION:words.append(PUNCTUATION[token]);cells+=1
        else: raise ValueError('Unsupported story character '+repr(token))
    return b''.join(struct.pack('<H',w) for w in words),cells,variables


def localize_script(rom, manifest):
    offset=int(manifest['asset_rom_offset'],16)
    destination=int(manifest.get('destination_rom_offset',hex(SCRIPT_DEST)),16)
    original,compressed_end=decode_lzss(rom,offset)
    assert len(original)==manifest.get('source_decoded_bytes',SCRIPT_SIZE)
    assert hashlib.sha256(original).hexdigest()==manifest['source_sha256']
    labels_start,second_table,code_base,code_size=struct.unpack_from('<4I',original)
    assert list(struct.unpack_from('<4I',original))==manifest.get('source_header',[16,384,400,6540])
    assert labels_start==16 and labels_start<=second_table<=code_base
    assert (second_table-labels_start)%4==0 and (code_base-second_table)%4==0
    assert code_base+code_size==len(original)
    edits=[];records=[]
    for item in manifest['strings']:
        start=int(item['offset'],16);raw=bytes.fromhex(item['source_hex']);end=start+len(raw)
        assert original[start:end]==raw,item['id']
        marker=int(item.get('marker','0x4005'),16)
        assert marker in (0x4003,0x4005)
        assert original[start-2:start]==struct.pack('<H',marker),item['id']+' print/choice opcode'
        assert end+2<=len(original) and struct.unpack_from('<H',original,end)[0]>=0x4000
        ids=struct.unpack('<'+'H'*(len(raw)//2),raw)
        assert all(w<0x4000 for w in ids)
        new,cells,variables=encode_story(item['english'])
        assert 0<item['max_cells']<=27 and cells<=item['max_cells'],(item['id'],cells)
        assert [w for w in ids if w>=0x1000]==[VARIABLES[v] for v in variables],item['id']+' variable integrity'
        edits.append((start,end,new))
        records.append({'id':item['id'],'page':item['page'],'line':item['line'],'old_offset':item['offset'],'cells_with_variable_budget':cells,'max_pixels':cells*8,'limit_pixels':item['max_cells']*8,'section':item.get('section','opening'),'role':item.get('role','dialogue'),'variables':variables,'verification':item['verification']})
    edits.sort()
    result=bytearray();position=0;new_positions={}
    for start,end,new in edits:
        assert start>=position
        result+=original[position:start]
        new_positions[start]=(len(result),len(result)+len(new))
        result+=new;position=end
    result+=original[position:]
    for record in records:
        new_start,new_end=new_positions[int(record['old_offset'],16)]
        record['new_offset']=hex(new_start);record['new_end']=hex(new_end)
    def relocated(address):
        delta=0
        for start,end,new in edits:
            if start<address<end: raise ValueError('Entry point inside edited text')
            if end<=address:delta+=len(new)-(end-start)
        return address+delta
    # Both original entry tables contain byte offsets relative to code_base.
    for p in range(labels_start,code_base,4):
        entry=struct.unpack_from('<I',original,p)[0]
        assert entry<code_size
        struct.pack_into('<I',result,p,relocated(code_base+entry)-code_base)
    struct.pack_into('<I',result,12,len(result)-code_base)
    def control_words(data):
        return [w[0] for w in struct.iter_unpack('<H',data[code_base:]) if w[0]>=0x4000]
    assert control_words(original)==control_words(result)
    packed=encode_lzss_literals(result)
    assert decode_lzss(packed)[0]==bytes(result)
    assert len(result)<0x10000,'The scenario must fit its 64 KiB event RAM area'
    pointer=struct.pack('<I',0x8000000+offset);references=[];p=0
    while True:
        p=rom.find(pointer,p)
        if p<0:break
        assert p%4==0 and (0x15E000<=p<0x161000 or 0x76E000<=p<0x76F000),hex(p)
        references.append(p);p+=4
    assert references
    if 'expected_pointer_offsets' in manifest:
        assert references==[int(p,16) for p in manifest['expected_pointer_offsets']]
    else:
        assert offset==SCRIPT_SOURCE and len(references)==1267
    report={'source_asset_rom_offset':hex(offset),'new_asset_rom_offset':hex(destination),'source_decoded_bytes':len(original),'new_decoded_bytes':len(result),'original_compressed_end':hex(compressed_end),'new_packed_bytes':len(packed),'entry_offsets_checked':(code_base-labels_start)//4,'vm_control_words_preserved':True,'player_name_variable_preserved':True,'line_records':len(records),'opening_pages':len({x['page'] for x in records if x['section']=='opening'}),'village_dialogue_pages':len({x['page'] for x in records if x['section']=='village' and x['role']=='dialogue' and x['cells_with_variable_budget']}),'village_choice_menus':len({x['menu'] for x in manifest['strings'] if x.get('section')=='village' and x.get('role')=='choice'}),'house_dialogue_pages':len({x['page'] for x in records if x['section']=='houses' and x['role']=='dialogue' and x['cells_with_variable_budget']}),'house_choice_menus':len({x['menu'] for x in manifest['strings'] if x.get('section')=='houses' and x.get('role')=='choice'}),'nonempty_english_lines':sum(bool(x['english']) for x in manifest['strings']),'pointer_count':len(references),'source_sha256':hashlib.sha256(original).hexdigest(),'localized_sha256':hashlib.sha256(result).hexdigest(),'records':records}
    sections={x['section'] for x in records}
    report['dialogue_pages_by_section']={section:len({x['page'] for x in records if x['section']==section and x['role']=='dialogue' and x['cells_with_variable_budget']}) for section in sorted(sections)}
    report['choice_menus_by_section']={section:len({x['menu'] for x in manifest['strings'] if x.get('section','opening')==section and x.get('role')=='choice'}) for section in sorted(sections)}
    return packed,references,report,bytes(result)
