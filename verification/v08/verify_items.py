import sys,json,hashlib,struct
from pathlib import Path
sys.path.insert(0,'analysis/v08');from verify_scene import *
MAP=json.loads((PROJECT/'verification_glyphs.json').read_text())['small_map']
def gid(char):
 if char==' ':return 0
 if 'a'<=char<='z':return 384+ord(char)-97
 return MAP[chr(ord(char)+0xfee0)] if 33<=ord(char)<=126 else MAP[char]
def small_mask(text):
 out=set()
 for i,char in enumerate(text):
  p=0x780000+gid(char)*32
  for y in range(8):
   for x in range(8):
    if DATA[p+y*4+x//2]>>(x%2*4)&15==2:out.add((8*i+x,y))
 return out
records=[]
def check(g,name,specs):
 im=g.image();im.save(ROOT/(name+'.png'))
 for identifier,text,x,y in specs:
  ink={(a,b) for b in range(8) for a in range(len(text)*8) if min(im.getpixel((x+a,y+b)))>200}
  assert small_mask(text)==ink,(identifier,x,y)
  records.append(dict(id=identifier,text=text,origin=[x,y],screenshot=name+'.png',pixel_match=True,capture_rom_sha256=hashlib.sha256(DATA).hexdigest()))
g=Game(ROM);g.load(ROOT/'medicine-field.state');press(g,256,120);press(g,1,90);press(g,1,90)
check(g,'final-medicine-name',[('item_healing_medicine','HP Med',96,16)])
press(g,1,90);press(g,1,90)
check(g,'final-medicine-target',[('battle_use_who','Use on whom?',80,24),('hp_before_healing','37',112,64)])
press(g,1,180);check(g,'final-medicine-effect',[('hp_recovered','28',80,72)]);g.close()
g=Game(ROM);g.load(ROOT/'healed-battle-start.state');check(g,'final-healed-battle',[('hp_after_healing','65',32,8)]);g.close()
source=Path('upload/Youkaidou (Japan).gba').read_bytes();offset=0x86430;original='かいふくやく\x01'.encode('shift_jis');extent=len(original)+1
assert len('HP Med')==6 and extent==14
assert DATA[offset+extent:0x86500]==source[offset+extent:0x86500]
ptr=struct.pack('<I',0x8000000+offset);references=[];p=0
while True:
 p=source.find(ptr,p)
 if p<0:break
 if p%2==0:assert DATA[p:p+4]==ptr;references.append(hex(p))
 p+=1
assert len(references)==58,len(references)
report=dict(target_rom_sha256=hashlib.sha256(DATA).hexdigest(),resolution=[240,160],records=records,healing_effect=dict(before_hp=37,recovered_hp=28,after_hp=65,normal_item_use=True),fixed_item_record=dict(name_cells=6,encoded_bytes_including_terminators=extent,following_item_data_unchanged=True,item_pointer_references_unchanged=references),all_pixel_checks_pass=True)
(ROOT/'item_pixel_checks.json').write_text(json.dumps(report,indent=2)+'\n');print('Item checks:',len(records),'exact text masks; HP 37 + 28 = 65; 58 item references and following metadata unchanged.')
