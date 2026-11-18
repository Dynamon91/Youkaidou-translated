import sys,ctypes as C,json,hashlib
sys.path.insert(0,'analysis/v07');from verify_scene import *
lib.load_save.argtypes=[C.c_void_p,C.c_char_p];lib.load_save.restype=C.c_int;lib.reset_game.argtypes=[C.c_void_p]
g=Game(ROM);source=PROJECT/'verification/v06/roundtrip.sav';assert lib.load_save(g.s,str(source).encode());lib.reset_game(g.s);g.frames(1200);press(g,8,90)
im=g.image()
def white(x,y):return sum(min(im.getpixel((x+a,y+b)))>200 for b in range(8) for a in range(7))
sel=[i for i in range(3) if white(88,88+16*i)==25];assert len(sel)==1
for _ in range((1-sel[0])%3):press(g,128,8)
press(g,1,240);g.screen(ROOT/'upgraded-v06-field.png');assert g.read(0x2010000,len(SCENES['departure_village']['decoded']))==SCENES['departure_village']['decoded']
g.frames(16,64);g.frames(240);assert g.read(0x2010000,len(SCENES['departure_houses']['decoded']))==SCENES['departure_houses']['decoded']
g.frames(8,64);g.frames(30);press(g,32,30);press(g,1);r=observe(g,'v06-save-upgraded-yayoi',True);assert r['scene']=='departure_houses' and r['page']==2
g.close()
result=dict(target_rom_sha256=hashlib.sha256(DATA).hexdigest(),source_v06_save_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),v06_save_loaded_after_reset=True,accepted_mission_preserved=True,upgraded_yayoi_page=2,all_pixel_checks_pass=True)
(ROOT/'upgrade_save_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
