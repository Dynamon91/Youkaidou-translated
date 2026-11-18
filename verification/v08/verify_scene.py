from pathlib import Path
import sys,json,hashlib,struct
sys.path.insert(0,'analysis/emulator');sys.path.insert(0,'github-save/repo')
from run import Game as RawGame,lib
class Game(RawGame):
 def load(self,path):
  super().load(path);self.frames(2)
from script_codec import encode_story
ROOT=Path('analysis/v08');PROJECT=Path('github-save/repo');OUT=ROOT/'output';ROM=OUT/'Youkaidou_English_v08.gba';DATA=ROM.read_bytes();V=json.loads((OUT/'validation.json').read_text());SCENES={};NAME_IDS=json.loads((PROJECT/'verification_glyphs.json').read_text())['default_player_name_glyphs'];SCREEN=ROOT/'screens';SCREEN.mkdir(exist_ok=True)
for name,manifests,report,decoded in [('village',['story_translations.json','village_translations.json'],V['story'],'localized_scenario.bin'),('houses',['house_translations.json'],V['houses'],'localized_houses.bin')]+[(n,[n+'_translations.json'],r,'localized_'+n+'.bin') for n,r in V['additional_scenarios'].items()]:
 items=[]
 for fn in manifests:
  for x in json.loads((PROJECT/fn).read_text())['strings']:
   x=dict(x);x.setdefault('section','opening');items.append(x)
 pages={};menus={}
 for x in items:
  if x.get('role','dialogue')=='dialogue':pages.setdefault((x['section'],x['page']),[]).append(x)
  elif x['role']=='choice':menus.setdefault((x['section'],x['menu']),[]).append(x)
 SCENES[name]=dict(items=items,report={x['id']:x for x in report['records']},decoded=(OUT/decoded).read_bytes(),pages=pages,menus=menus)
def mask(text,width=27):
 ids=[]
 for (g,) in struct.iter_unpack('<H',encode_story(text)[0]):ids.extend(NAME_IDS if g==0x1000 else [g])
 assert len(ids)<=width;out=set()
 for i,g in enumerate(ids):
  p=0x770000+g//10*640+g%10*32
  for y in range(16):
   for x in range(8):
    if (DATA[p+y//8*320+y%8*4+x//2]>>(x%2*4)&15)==1:out.add((i*8+x,y))
 return out
def ink(im,line,width=27,selected=False):return {(x,y) for y in range(16) for x in range(width*8) if (max(im.getpixel((8+x,120+line*16+y)))<50 if selected else min(im.getpixel((8+x,120+line*16+y)))>200)}
for s in SCENES.values():s['masks']={k:[mask(next((x['english'] for x in items if x['line']==ln),'')) for ln in [1,2]] for k,items in s['pages'].items() if any(x['english'] for x in items)}
def observe(g,label,required=False):
 im=g.image();pc=lib.read32(g.s,0x300325c)-0x2010000;header=g.read(0x2010000,16);found=None
 for name,s in [(n,s) for n,s in SCENES.items() if s['decoded'][:16]==header]:
  def distance(items):return min(abs(pc-int(s['report'][x['id']]['new_end'],16)) for x in items)
  options=[]
  for key,items in s['menus'].items():
   for selected in [0,1]:
    if distance(items)<=64 and all(mask(x['english'],len(x['english']))==ink(im,i,len(x['english']),i==selected) for i,x in enumerate(items)):options.append((distance(items),key,selected,items))
  if options:
   delta,key,selected,items=min(options);found=dict(kind='choice',section=key[0],menu=key[1],selected=selected,records=[x['id'] for x in items],text=[x['english'] for x in items])
  else:
   got=[ink(im,i) for i in range(2)];pages=[k for k,want in s['masks'].items() if want==got and distance(s['pages'][k])<=64]
   if pages:
    key=min(pages,key=lambda k:distance(s['pages'][k]));items=s['pages'][key];found=dict(kind='dialogue',section=key[0],page=key[1],records=[x['id'] for x in items],text=[next((x['english'] for x in items if x['line']==ln),'') for ln in [1,2]])
  if found:
   assert g.read(0x2010000,len(s['decoded']))==s['decoded'],'Scenario RAM differs from final stream'
   p=SCREEN/(label+'.png');im.save(p);g.save(SCREEN/(label+'.state'));found.update(label=label,scene=name,screenshot=str(p),script_pc=hex(pc),pixel_match=True,rom_sha256=hashlib.sha256(DATA).hexdigest(),scenario_sha256=hashlib.sha256(s['decoded']).hexdigest())
   file=ROOT/'capture_log.json';log=json.loads(file.read_text()) if file.exists() else [];log=[x for x in log if x['label']!=label]+[found];file.write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n');print(label,found['section'],found['kind'],found.get('page',found.get('menu')),flush=True);return found
 if required:im.save(SCREEN/(label+'-unmatched.png'));raise AssertionError('No text match '+label+' pc='+hex(pc)+' header='+header.hex())
 return None
def press(g,key,wait=840):g.frames(3,key);g.frames(wait)
