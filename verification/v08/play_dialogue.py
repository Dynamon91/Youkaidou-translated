import sys
sys.path.insert(0,'analysis/v08');from verify_scene import *
def drain(g,prefix,limit=70):
 for i in range(limit):
  r=observe(g,f'{prefix}-{i:02d}')
  if r is None:
   g.frames(840);r=observe(g,f'{prefix}-{i:02d}')
  if r is None:
   g.screen(ROOT/f'{prefix}-field.png');g.save(ROOT/f'{prefix}-field.state');return None
  if r['kind']=='choice':
   g.save(ROOT/f'{prefix}-menu.state');return r
  press(g,1)
 raise AssertionError('Dialogue loop limit')
if __name__=='__main__':
 g=Game(ROM);g.load(sys.argv[1]);r=drain(g,sys.argv[2]);print('STOP',r,flush=True);g.close()
