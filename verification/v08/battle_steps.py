import sys
from pathlib import Path
from PIL import Image
sys.path.insert(0,'analysis/v08');from verify_scene import *
def cell(im,row,col):return im.crop((18+col*16,98+row*16,30+col*16,110+row*16)).tobytes()
ref=Image.open('analysis/v07/final-ittan-battle.png').convert('RGB')
sword=cell(ref,3,0);guard=cell(ref,3,2)
def groups(im,template):
 cells={(r,c) for r in range(4) for c in range(5) if cell(im,r,c)==template};options=[]
 for c in range(5):
  if (3,c) not in cells:continue
  found={(3,c)};todo=list(found)
  while todo:
   r,k=todo.pop()
   for n in [(r-1,k),(r+1,k),(r,k-1),(r,k+1)]:
    if n in cells and n not in found:found.add(n);todo.append(n)
  options.append((len(found),c))
 return sorted(options,reverse=True)
def action(g,col):
 for _ in range(5-col):press(g,32,20)
 press(g,1,2400)
if __name__=='__main__':
 g=Game(ROM);g.load(sys.argv[1]);prefix=sys.argv[2]
 for i,token in enumerate(sys.argv[3:]):
  im=g.image();print(i,'Sword',groups(im,sword),'Guard',groups(im,guard),flush=True)
  col=groups(im,sword)[0][1] if token=='S' else groups(im,guard)[0][1] if token=='G' else int(token)
  action(g,col);g.screen(ROOT/f'{prefix}-{i}.png');g.save(ROOT/f'{prefix}-{i}.state');observe(g,f'{prefix}-{i}')
 g.close()
