#!/usr/bin/env python3
"""Build the Youkaidou English UI and event scenarios from a clean AFUJ ROM."""
from pathlib import Path
import argparse, hashlib, json, struct
from script_codec import localize_script, decode_lzss, SCRIPT_DEST

SOURCE_SHA256 = '080a70324ee02c0ef850fccec0c2353faff4598e1f18cdf35277f5c05ba3ce06'
FONT_SOURCE = 0x2A98C8
FONT_SIZE = 0xFA00
FONT_DEST = 0x770000
TEXT_DEST = 0x788000
SMALL_FONT_DEST = 0x780000
SMALL_LOWERCASE_START = 0x180
LOWERCASE_START = 0x320
FONT_POINTERS = [0x5BFC, 0xE1AC, 0x78A80, 0x7B568, 0x5589C4]
# Each pattern is a 5x7 original pixel design. The glyph has the same 8x16 cell
# and baseline as the original font; lowercase ascenders and descenders differ.
LOWER = {
'a':['00000','00000','01110','00001','01111','10001','01111'],
'b':['10000','10000','10110','11001','10001','10001','11110'],
'c':['00000','00000','01110','10000','10000','10000','01110'],
'd':['00001','00001','01101','10011','10001','10001','01111'],
'e':['00000','00000','01110','10001','11111','10000','01110'],
'f':['00110','01001','01000','11100','01000','01000','01000'],
'g':['00000','00000','01111','10001','10001','10001','01111','00001','01110'],
'h':['10000','10000','10110','11001','10001','10001','10001'],
'i':['00100','00000','01100','00100','00100','00100','01110'],
'j':['00010','00000','00110','00010','00010','00010','00010','10010','01100'],
'k':['10000','10000','10010','10100','11000','10100','10010'],
'l':['01100','00100','00100','00100','00100','00100','01110'],
'm':['00000','00000','11010','10101','10101','10101','10101'],
'n':['00000','00000','10110','11001','10001','10001','10001'],
'o':['00000','00000','01110','10001','10001','10001','01110'],
'p':['00000','00000','11110','10001','10001','10001','11110','10000','10000'],
'q':['00000','00000','01111','10001','10001','10001','01111','00001','00001'],
'r':['00000','00000','10110','11001','10000','10000','10000'],
's':['00000','00000','01111','10000','01110','00001','11110'],
't':['01000','01000','11100','01000','01000','01001','00110'],
'u':['00000','00000','10001','10001','10001','10011','01101'],
'v':['00000','00000','10001','10001','10001','01010','00100'],
'w':['00000','00000','10001','10001','10101','10101','01010'],
'x':['00000','00000','10001','01010','00100','01010','10001'],
'y':['00000','00000','10001','10001','10001','10011','01101','00001','01110'],
'z':['00000','00000','11111','00010','00100','01000','11111'],
}

def encode(text):
    result = bytearray()
    for char in text:
        if ord(char) < 32:
            result.append(ord(char))
        elif char == ' ':
            result.extend('\u3000'.encode('shift_jis'))
        elif '!' <= char <= '~':
            result.extend(chr(ord(char) + 0xFEE0).encode('shift_jis'))
        else:
            result.extend(char.encode('shift_jis'))
    return bytes(result)

def make_font(source):
    rows = max(FONT_SIZE // 640, (LOWERCASE_START + 26 + 9) // 10)
    data = bytearray([0x44]) * (rows * 640)
    data[:FONT_SIZE] = source[FONT_SOURCE:FONT_SOURCE+FONT_SIZE]
    for number, (char, pattern) in enumerate(LOWER.items()):
        glyph = LOWERCASE_START + number
        pixels = [[4] * 8 for _ in range(16)]
        # Ascenders use the cap line; x-height remains lower than capitals.
        # Descenders use the last two rows of the 16-pixel cell.
        y0 = 7
        for y, row in enumerate(pattern):
            for x, bit in enumerate(row):
                if bit == '1': pixels[y0+y][1+x] = 1
        for y in range(15, -1, -1):
            for x in range(7, -1, -1):
                if pixels[y][x] == 1 and x < 7 and y < 15 and pixels[y+1][x+1] == 4:
                    pixels[y+1][x+1] = 2
        origin = (glyph // 10) * 640 + (glyph % 10) * 32
        for y in range(16):
            for x in range(0, 8, 2):
                data[origin + (y//8)*320 + (y%8)*4 + x//2] = pixels[y][x] | pixels[y][x+1]<<4
    return data

def ips(before, after):
    assert len(before) == len(after)
    out = bytearray(b'PATCH')
    i = 0
    while i < len(after):
        if before[i] == after[i]: i += 1; continue
        start = i
        # Merge small unchanged gaps to keep the patch compact.
        last = i
        while i < len(after) and i - start < 65535:
            if before[i] != after[i]: last = i
            elif i-last >= 8: break
            i += 1
        end = last+1
        out += start.to_bytes(3, 'big') + (end-start).to_bytes(2, 'big') + after[start:end]
        i = end
    return out + b'EOF'

def apply_ips(source, patch):
    assert patch[:5] == b'PATCH'
    b = bytearray(source); p=5
    while patch[p:p+3] != b'EOF':
        addr = int.from_bytes(patch[p:p+3], 'big'); size = int.from_bytes(patch[p+3:p+5], 'big'); p += 5
        if size:
            b[addr:addr+size] = patch[p:p+size]; p += size
        else:
            n = int.from_bytes(patch[p:p+2], 'big'); value = patch[p+2]; p += 3
            b[addr:addr+n] = bytes([value])*n
    return bytes(b)

def build(path, out):
    source = path.read_bytes()
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA256:
        raise SystemExit('Wrong source ROM. This batch requires the exact unmodified ROM identified in README.md.')
    manifest = json.loads((Path(__file__).parent/'translations.json').read_text())
    if (out/'Youkaidou_English_v07.gba').resolve() == path.resolve():
        raise SystemExit('The output must not overwrite the input ROM.')
    patched = bytearray(source); font = make_font(source)
    assert all(x == 0 for x in source[FONT_DEST:FONT_DEST+len(font)])
    patched[FONT_DEST:FONT_DEST+len(font)] = font
    for location in FONT_POINTERS:
        assert source[location:location+4] == struct.pack('<I',0x8000000+FONT_SOURCE)
        patched[location:location+4] = struct.pack('<I',0x8000000+FONT_DEST)
    # The stock converter aliases a-z to A-Z. Give a-z their own glyph IDs.
    for converter, start in [(0x4AAC,SMALL_LOWERCASE_START),(0x6EA90,LOWERCASE_START)]:
        assert source[converter:converter+4] == struct.pack('<I',0x7DA0)
        patched[converter:converter+4] = struct.pack('<I',(start-0x8281)&0xFFFF)
    small = bytearray(decode_lzss(source,0x765F44)[0])
    assert len(small) == 0x4000
    assert hashlib.sha256(small).hexdigest() == '6815e215b19d73a7ed90f396862a063a5432dfc35e6b5bd01bb7ed7edb2fbbc8'
    assert not any(small[SMALL_LOWERCASE_START*32:(SMALL_LOWERCASE_START+26)*32])
    for number, (char, pattern) in enumerate(LOWER.items()):
        cell = [[1]*8 for _ in range(8)]
        if len(pattern) > 7:
            pattern = [pattern[0],pattern[1],pattern[2],pattern[3],pattern[6],pattern[7],pattern[8]]
        for y,row in enumerate(pattern):
            for x,bit in enumerate(row):
                if bit=='1': cell[y+1][x+1]=2
        origin = (SMALL_LOWERCASE_START+number)*32
        for y in range(8):
            for x in range(0,8,2):
                small[origin+y*4+x//2]=cell[y][x] | cell[y][x+1]<<4
    assert source[0x2EC:0x2F0] == bytes.fromhex('05f024ff')
    assert source[0x358:0x35C] == struct.pack('<I',0x02032004)
    # The bootstrap copies this immutable 16 KiB tile bank. Replace its
    # decompression call with the identical output length and a ROM bank pointer.
    patched[0x2EC:0x2F0] = bytes.fromhex('8020c001')
    patched[0x358:0x35C] = struct.pack('<I',0x8000000+SMALL_FONT_DEST)
    assert not any(source[SMALL_FONT_DEST:SMALL_FONT_DEST+len(small)])
    patched[SMALL_FONT_DEST:SMALL_FONT_DEST+len(small)] = small
    # The main menu calculates its width from the longest label. Its original
    # x=22 clips the wider English labels; x=18 keeps the right edge at tile 30.
    assert source[0x61EC6:0x61EC8] == bytes.fromhex('1622')
    patched[0x61EC6:0x61EC8] = bytes.fromhex('1222')
    cursor = TEXT_DEST; records=[]
    for item in manifest['strings']:
        offset = int(item['offset'],16)
        original = bytes.fromhex(item['source_hex'])
        assert source[offset:offset+len(original)] == original, item['id']
        assert original.decode('shift_jis') == item['japanese'], item['id']
        english = item['english']
        assert ''.join(c for c in english if ord(c)<32) == ''.join(c for c in item['japanese'] if ord(c)<32), item['id']+' control sequence'
        segments = english.replace('\x01','').split('\n\n\n\n')
        for segment in segments:
            assert len(segment) <= item['max_cells'], (item['id'], segment, len(segment), item['max_cells'])
            if 'prefix_budget_cells' in item:
                assert len(segment)+item['prefix_budget_cells']<=item['total_cell_limit'],item['id']+' composed popup limit'
        raw = encode(english)+b'\0'
        ptr = struct.pack('<I',0x8000000+offset)
        refs=[]; p=0
        while True:
            p=source.find(ptr,p)
            if p<0: break
            if p % 2 == 0: refs.append(p)
            p+=1
        assert refs, item['id']+' has no validated aligned references'
        all_refs = refs
        if 'reference_offsets' in item:
            refs = [int(p,16) for p in item['reference_offsets']]
            assert len(refs)==len(set(refs)) and set(refs)<=set(all_refs),item['id']+' reference scope'
        cursor = (cursor+3)&~3
        assert not any(source[cursor:cursor+len(raw)]), 'destination is not empty'
        patched[cursor:cursor+len(raw)] = raw
        for reference in refs:
            assert patched[reference:reference+4] == ptr
            patched[reference:reference+4] = struct.pack('<I',0x8000000+cursor)
        for reference in all_refs:
            if reference not in refs:
                assert patched[reference:reference+4] == ptr,item['id']+' changed an unrelated reference'
        records.append({'id':item['id'],'old_offset':item['offset'],'new_offset':hex(cursor),'pointers':[hex(r) for r in refs],'untouched_references':[hex(r) for r in all_refs if r not in refs],'new_bytes':len(raw),'max_line_cells':max(map(len,segments)),'max_line_pixels':8*max(map(len,segments)),'limit_pixels':8*item['max_cells'],'verification':item['verification']})
        cursor += len(raw)
    ui = {x['id']:x['english'].replace('\x01','') for x in manifest['strings']}
    level_cells = 8+len(ui['level_up_subject_link'])+len(ui['level_up_level_label'])+3+len(ui['level_up_result_end'])
    stat_ids = ['level_up_attack','level_up_defense','level_up_magic','level_up_magic_defense','level_up_speed','level_up_luck']
    stat_cells = max(len(ui[x]) for x in stat_ids)+len(ui['level_up_stat_value_link'])+6+len(ui['level_up_result_end'])
    assert level_cells<=24 and stat_cells<=24,'Composed level-up popup exceeds its cell budget'
    story_manifest = json.loads((Path(__file__).parent/'story_translations.json').read_text())
    village_manifest = json.loads((Path(__file__).parent/'village_translations.json').read_text())
    assert village_manifest['source_sha256']==story_manifest['source_sha256']
    combined_manifest=dict(story_manifest, strings=story_manifest['strings']+village_manifest['strings'])
    packed, references, story_report, localized_script = localize_script(source,combined_manifest)
    assert not any(source[SCRIPT_DEST:SCRIPT_DEST+len(packed)])
    patched[SCRIPT_DEST:SCRIPT_DEST+len(packed)] = packed
    for reference in references:
        assert source[reference:reference+4] == struct.pack('<I',0x8000000+int(story_manifest['asset_rom_offset'],16))
        patched[reference:reference+4] = struct.pack('<I',0x8000000+SCRIPT_DEST)
    house_manifest = json.loads((Path(__file__).parent/'house_translations.json').read_text())
    house_packed, house_references, house_report, localized_houses = localize_script(source,house_manifest)
    house_dest = int(house_manifest['destination_rom_offset'],16)
    assert SCRIPT_DEST+len(packed)<=house_dest
    assert house_dest+len(house_packed)<len(source)
    assert not any(patched[house_dest:house_dest+len(house_packed)])
    patched[house_dest:house_dest+len(house_packed)] = house_packed
    for reference in house_references:
        assert patched[reference:reference+4] == struct.pack('<I',0x8000000+int(house_manifest['asset_rom_offset'],16))
        patched[reference:reference+4] = struct.pack('<I',0x8000000+house_dest)
    additional_reports = {};additional_decoded = {}
    occupied_end = house_dest+len(house_packed)
    for name in ['shrine','return','elder_story','supply_village','supply_houses','departure_village','departure_houses','cargo_road','cargo_village','cargo_report','journey_village']:
        event_manifest = json.loads((Path(__file__).parent/(name+'_translations.json')).read_text())
        event_packed,event_refs,event_report,event_decoded = localize_script(source,event_manifest)
        destination = int(event_manifest['destination_rom_offset'],16)
        assert occupied_end<=destination and destination+len(event_packed)<=len(source)
        assert not any(patched[destination:destination+len(event_packed)])
        patched[destination:destination+len(event_packed)] = event_packed
        for reference in event_refs:
            assert patched[reference:reference+4]==struct.pack('<I',0x8000000+int(event_manifest['asset_rom_offset'],16))
            patched[reference:reference+4]=struct.pack('<I',0x8000000+destination)
        occupied_end=destination+len(event_packed)
        additional_reports[name]=event_report;additional_decoded[name]=event_decoded
    assert source[:0xC0] == patched[:0xC0]
    assert len(source) == len(patched)
    assert font[:800*64] == source[FONT_SOURCE:FONT_SOURCE+800*64]
    patch = ips(source,patched)
    assert apply_ips(source,patch) == patched
    out.mkdir(parents=True,exist_ok=True)
    (out/'Youkaidou_English_v07.gba').write_bytes(patched)
    (out/'Youkaidou_English_v07.ips').write_bytes(patch)
    report = {'stage':'English v07: delivery rescue, return journey and war warning; partial localization','source_sha256':SOURCE_SHA256,'output_sha256':hashlib.sha256(patched).hexdigest(),'rom_size':len(patched),'translated_strings':len(records),'lowercase_glyphs':26,'existing_8x16_glyphs_preserved':800,'existing_8x8_font_bank_unchanged_outside_lowercase_slots':True,'font_sizes':['8x8','8x16'],'header_unchanged':True,'control_sequences_preserved':True,'patch_roundtrip_verified':True,'main_menu_layout':{'x_tiles':18,'width_tiles':12,'right_edge_pixels':240,'longest_label_cells':9},'screen_checked_string_count':sum(x['verification'].startswith('Observed') for x in manifest['strings']),'static_only_string_count':sum(not x['verification'].startswith('Observed') for x in manifest['strings']),'story':story_report,'houses':house_report,'records':records}
    report['level_up_layout'] = {'name_budget_cells':8,'level_digits':3,'stat_digits_with_sign':6,'level_sentence_max_cells':level_cells,'stat_sentence_max_cells':stat_cells,'limit_cells':24,'reference_scope':'Only level-up call sites; shared Japanese particles and fixed-field stat paths are preserved elsewhere'}
    (out/'localized_scenario.bin').write_bytes(localized_script)
    (out/'localized_houses.bin').write_bytes(localized_houses)
    report['additional_scenarios'] = additional_reports
    for name,event_decoded in additional_decoded.items():
        (out/('localized_'+name+'.bin')).write_bytes(event_decoded)
    (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['records','story','houses','additional_scenarios']},indent=2))

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('rom',type=Path);p.add_argument('--output',type=Path,default=Path(__file__).parent/'output')
    a=p.parse_args();build(a.rom,a.output)
