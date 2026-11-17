import sys,ctypes as C,json,hashlib
sys.path.insert(0,'analysis/v06');from verify_scene import *
lib.load_save.argtypes=[C.c_void_p,C.c_char_p];lib.load_save.restype=C.c_int;lib.reset_game.argtypes=[C.c_void_p]
g=Game(ROM);g.load(ROOT/'continued.state');g.frames(16,64);g.frames(240)
assert g.read(0x2010000,len(SCENES['departure_houses']['decoded']))==SCENES['departure_houses']['decoded']
g.frames(8,64);g.frames(30);press(g,32,30);press(g,1);rec=observe(g,'saved-mission-yayoi',True);assert rec['scene']=='departure_houses' and rec['page']==2
g.close()
# Load the actual v05 backup, reset, choose Continue by reading its cursor.
g=Game(ROM);assert lib.load_save(g.s,b'github-save/repo/verification/roundtrip.sav');lib.reset_game(g.s);g.frames(1200);press(g,8,90)
im=g.image()
def white(x,y):return sum(min(im.getpixel((x+a,y+b)))>200 for b in range(8) for a in range(7))
sel=[i for i in range(3) if white(88,88+16*i)==25];assert len(sel)==1
for _ in range((1-sel[0])%3):press(g,128,8)
press(g,1,240);g.screen(ROOT/'upgraded-v05-field.png');assert g.read(0x2010000,len(SCENES['return']['decoded']))==SCENES['return']['decoded']
g.frames(16,64);g.frames(240);assert g.read(0x2010000,len(SCENES['elder_story']['decoded']))==SCENES['elder_story']['decoded']
g.frames(8,64);g.frames(30);press(g,32,30);press(g,1);r=observe(g,'v05-save-upgraded-yayoi',True);assert r['scene']=='elder_story' and r['page']==11
g.close()
result=dict(target_rom_sha256=hashlib.sha256(DATA).hexdigest(),post_mission_save_continued=True,accepted_mission_preserved=True,continued_yayoi_page=2,source_v05_save_sha256=hashlib.sha256((PROJECT/'verification/roundtrip.sav').read_bytes()).hexdigest(),v05_save_loaded_after_reset=True,v05_shrine_stage_preserved=True,upgraded_yayoi_page=11,all_pixel_checks_pass=True)
(ROOT/'upgrade_save_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
