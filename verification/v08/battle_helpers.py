from pathlib import Path
import json
from PIL import Image
from verify_scene import DATA,press
MAP=json.loads(Path('github-save/repo/verification_glyphs.json').read_text())['small_map']
def smallmask(text):
 out=set()
 for i,c in enumerate(text):
  g=MAP[c];p=0x780000+g*32
  for y in range(8):
   for x in range(8):
    if DATA[p+y*4+x//2]>>(x%2*4)&15==2:out.add((i*8+x,y))
 return out
def find_word(im,text,top=88):
 want=smallmask(text);w=len(text)*8;white={(x,y) for y in range(top,160) for x in range(240) if min(im.getpixel((x,y)))>200};ans=[]
 for y in range(top,153):
  for x in range(241-w):
   if all(((x+a,y+b) in white)==((a,b) in want) for b in range(8) for a in range(w)):ans.append((x,y))
 return ans
if __name__=='__main__':
 for file,text in [('wild-left-choice','こうげき'),('wild-next-card','なし')]:
  im=Image.open('analysis/v07/'+file+'.png').convert('RGB');print(file,text,find_word(im,text,136))
