import sys,ctypes as C,json,hashlib
sys.path.insert(0,'analysis/v08');from verify_scene import *
lib.load_save.argtypes=[C.c_void_p,C.c_char_p];lib.load_save.restype=C.c_int;lib.reset_game.argtypes=[C.c_void_p]
# Confirm that the new quest stage survived a completed v08 save and reset.
g=Game(ROM);g.load(ROOT/'continued.state');assert g.read(0x2010000,len(SCENES['journey_village']['decoded']))==SCENES['journey_village']['decoded'];g.screen(ROOT/'continued-journey-stage.png');g.close()
# Upgrade the actual v07 delivery-road save without changing its data.
source=PROJECT/'verification/v07/roundtrip.sav';g=Game(ROM);assert lib.load_save(g.s,str(source).encode());lib.reset_game(g.s);g.frames(1200);press(g,8,90);im=g.image()
def white(x,y):return sum(min(im.getpixel((x+a,y+b)))>200 for b in range(8) for a in range(7))
sel=[i for i in range(3) if white(88,88+16*i)==25];assert len(sel)==1
for _ in range((1-sel[0])%3):press(g,128,8)
press(g,1,240);assert g.read(0x2010000,len(SCENES['cargo_road']['decoded']))==SCENES['cargo_road']['decoded'];g.screen(ROOT/'upgraded-v07-field.png');press(g,128,150);press(g,1);r=observe(g,'v07-save-upgraded-driver',True);assert r['scene']=='cargo_road' and r['page']==1;g.close()
result=dict(target_rom_sha256=hashlib.sha256(DATA).hexdigest(),new_quest_stage_preserved_after_v08_reset=True,continued_scenario='journey_village',source_v07_save_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),v07_save_loaded_after_reset=True,old_delivery_mission_preserved=True,upgraded_driver_page=1,all_pixel_checks_pass=True)
(ROOT/'upgrade_save_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
