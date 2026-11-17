import ctypes as C
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
lib=C.CDLL(str(ROOT/'bridge.so'))
for name,args,rest in [('open_game',[C.c_char_p],C.c_void_p),('close_game',[C.c_void_p],None),('frames',[C.c_void_p,C.c_int,C.c_uint32],None),('pixels',[C.c_void_p],C.c_void_p),('pixel_size',[],C.c_int),('read8',[C.c_void_p,C.c_uint32],C.c_uint32),('read16',[C.c_void_p,C.c_uint32],C.c_uint32),('read32',[C.c_void_p,C.c_uint32],C.c_uint32),('write8',[C.c_void_p,C.c_uint32,C.c_uint32],None),('raw8',[C.c_void_p,C.c_uint32,C.c_uint32],None),('dump',[C.c_void_p,C.c_uint32,C.c_void_p,C.c_int],None),('reg',[C.c_void_p,C.c_char_p],C.c_uint32),('state_size',[C.c_void_p],C.c_size_t),('save_state',[C.c_void_p,C.c_void_p],C.c_int),('load_state',[C.c_void_p,C.c_void_p],C.c_int),('step_one',[C.c_void_p],None)]:
 f=getattr(lib,name);f.argtypes=args;f.restype=rest
class Game:
 def __init__(self,path):
  self.s=lib.open_game(str(path).encode());assert self.s,'ROM load failed'
 def frames(self,n,keys=0):lib.frames(self.s,n,keys)
 def image(self):
  data=C.string_at(lib.pixels(self.s),240*160*lib.pixel_size())
  return Image.frombytes('RGBA',(240,160),data).convert('RGB')
 def screen(self,path):self.image().save(path)
 def read(self,addr,n):
  out=C.create_string_buffer(n);lib.dump(self.s,addr,out,n);return out.raw
 def save(self,path):
  out=C.create_string_buffer(lib.state_size(self.s));assert lib.save_state(self.s,out);Path(path).write_bytes(out.raw)
 def load(self,path):
  out=C.create_string_buffer(Path(path).read_bytes());assert lib.load_state(self.s,out)
 def close(self):lib.close_game(self.s)
if __name__=='__main__':
 import sys
 g=Game(sys.argv[1]);g.frames(300);g.screen('analysis/original-title.png');g.frames(1,8);g.frames(30);g.screen('analysis/original-menu.png');g.save('analysis/menu.state');
 for a,n in [(0x6000000,0x18000),(0x5000000,0x400),(0x4000000,0x60),(0x2000000,0x40000),(0x3000000,0x8000)]:Path(f'analysis/memory-{a:08x}.bin').write_bytes(g.read(a,n))
 print('pixel_size',lib.pixel_size(),'pc',hex(lib.reg(g.s,b'pc')))
 g.close()
