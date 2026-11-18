from pathlib import Path
import sys,ctypes as C,json
from PIL import Image
sys.path.insert(0,str(Path('analysis/emulator').resolve()))
from run import Game,lib
lib.dump_save.argtypes=[C.c_void_p,C.c_char_p];lib.dump_save.restype=C.c_size_t
lib.load_save.argtypes=[C.c_void_p,C.c_char_p];lib.load_save.restype=C.c_int
lib.reset_game.argtypes=[C.c_void_p]
rom='analysis/v08/output/Youkaidou_English_v08.gba';root=Path('analysis/v08/final-ui');root.mkdir(exist_ok=True)
ref=Image.open('github-save/repo/screenshots/save-v05/save-confirm.png').convert('RGB')
def mask(im,x,y,w,h):return {(a,b) for b in range(h) for a in range(w) if min(im.getpixel((x+a,y+b)))>200}
yes_mask=mask(ref,56,104,24,8);no_mask=mask(ref,56,120,16,8);arrow=mask(ref,48,104,7,8)
assert len(arrow)==25
choices=[]
def press(k,w=90):g.frames(3,k);g.frames(w)
def choose(yes):
 im=g.image();found=[]
 for y in range(0,137,8):
  for x in range(8,217,8):
   if mask(im,x,y,24,8)==yes_mask and mask(im,x,y+16,16,8)==no_mask:found.append((x,y))
 assert len(found)==1,found
 x,y=found[0];is_yes=mask(im,x-8,y,7,8)==arrow;is_no=mask(im,x-8,y+16,7,8)==arrow
 assert is_yes != is_no
 if is_yes!=yes:press(128,8)
 im=g.image();assert mask(im,x-8,y+(0 if yes else 16),7,8)==arrow
 choices.append({'requested':'Yes' if yes else 'No','observed_before_press':'Yes' if is_yes else 'No','matched_after_navigation':True})
 press(1,1200 if yes else 120)
def open_save():
 press(256,45)
 # Read the seven-row field-menu cursor, which can remember its last position.
 im=g.image();sel=[mask(im,152,24+i*16,7,8)==arrow for i in range(7)];assert sum(sel)==1,sel
 current=sel.index(True)
 for _ in range((5-current)%7):press(128,8)
 press(1,120)
# Cancel from a fresh session; no save write is started.
g=Game(rom);g.load('analysis/v08/journey-field.state');g.frames(2);open_save();g.screen(root/'save-confirm.png');choose(False);g.screen(root/'save-cancelled.png');g.close()
# Write a complete save in a separate fresh session.
g=Game(rom);g.load('analysis/v08/journey-field.state');g.frames(2);open_save();choose(True);g.screen(root/'save-complete.png');n=lib.dump_save(g.s,b'analysis/v08/roundtrip.sav');assert n==8192;g.close()
# Reset and Continue from that actual backup, then prove the field menu opens.
g=Game(rom);assert lib.load_save(g.s,b'analysis/v08/roundtrip.sav');lib.reset_game(g.s);g.frames(1200);press(8,90);im=g.image();im.save(root/'title-with-save.png')
sel=[mask(im,88,88+16*i,7,8)==arrow for i in range(3)];assert sum(sel)==1,sel
for _ in range((1-sel.index(True))%3):press(128,8)
press(1,240);g.screen(root/'continue-game.png');g.save('analysis/v08/continued.state');press(256,45);g.screen(root/'continued-field-menu.png')
reference=Image.open('github-save/repo/screenshots/save-v05/continued-field-menu.png').convert('RGB');assert g.image().crop((160,24,232,128)).tobytes()==reference.crop((160,24,232,128)).tobytes(),'Continue did not reach a working field menu'
# Close the field menu and request another save to exercise the overwrite prompt.
press(2,45);open_save();g.screen(root/'save-again-confirm.png');choose(True);g.screen(root/'overwrite-confirm.png');choose(False);g.screen(root/'overwrite-cancelled.png');g.close()
result={'backup_bytes':n,'fresh_reset_loaded_save':True,'continue_reached_gameplay':True,'continued_field_menu_pixel_match':True,'confirmation_choices':choices,'screens':['save-confirm.png','save-cancelled.png','save-complete.png','title-with-save.png','continue-game.png','continued-field-menu.png','save-again-confirm.png','overwrite-confirm.png','overwrite-cancelled.png']}
Path('analysis/v08/save_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
