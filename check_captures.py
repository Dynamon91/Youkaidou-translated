"""Check archived emulator text captures against the release ROM's font pixels.

Requires Pillow. This checks the supplied captures; it does not replay gameplay.
"""
from pathlib import Path
import json,struct
from PIL import Image
from script_codec import encode_story

ROOT=Path(__file__).resolve().parent
ROM=(ROOT/'Youkaidou_English_v06.gba').read_bytes()
GLYPHS=json.loads((ROOT/'verification_glyphs.json').read_text())

def large_mask(text,width=27):
    ids=[]
    for (gid,) in struct.iter_unpack('<H',encode_story(text)[0]):
        ids.extend(GLYPHS['default_player_name_glyphs'] if gid==0x1000 else [gid])
    assert len(ids)<=width
    result=set()
    for i,gid in enumerate(ids):
        p=0x770000+gid//10*640+gid%10*32
        for y in range(16):
            for x in range(8):
                if (ROM[p+y//8*320+y%8*4+x//2]>>(x%2*4)&15)==1:result.add((i*8+x,y))
    return result

def image_ink(im,x,y,width,height,black=False):
    return {(a,b) for b in range(height) for a in range(width)
            if (max(im.getpixel((x+a,y+b)))<50 if black
                else min(im.getpixel((x+a,y+b)))>200)}

def small_glyph(char):
    if char==' ':return 0
    if 'a'<=char<='z':return 384+ord(char)-97
    if 33<=ord(char)<=126:return GLYPHS['small_map'][chr(ord(char)+0xfee0)]
    return GLYPHS['small_map'][char]

def small_mask(text):
    result=set()
    for i,char in enumerate(text):
        p=0x780000+small_glyph(char)*32
        for y in range(8):
            for x in range(8):
                if (ROM[p+y*4+x//2]>>(x%2*4)&15)==2:result.add((i*8+x,y))
    return result

pages=choices=popups=0
for filename in ['opening_pixel_checks.json','village_pixel_checks.json','house_pixel_checks.json','story_pixel_checks.json','mission_pixel_checks.json']:
    data=json.loads((ROOT/filename).read_text())
    for page in data['pages']:
        im=Image.open(ROOT/page['screenshot']).convert('RGB')
        assert im.size==(240,160)
        for line in page['lines']:
            want=large_mask(line['text']);got=image_ink(im,8,120+(line['line']-1)*16,216,16)
            assert want==got,(filename,page['page'],line['line'],len(want-got),len(got-want))
        pages+=1
    for choice in data.get('choices',[]):
        im=Image.open(ROOT/choice['screenshot']).convert('RGB')
        for index,line in enumerate(choice['lines']):
            width=len(line['text']);want=large_mask(line['text'],width)
            got=image_ink(im,8,120+index*16,width*8,16,line['selected'])
            assert want==got,(filename,'choice',line['text'])
        choices+=1
for popup in json.loads((ROOT/'level_up_pixel_checks.json').read_text())['records']:
    im=Image.open(ROOT/popup['screenshot']).convert('RGB');x,y=popup['origin']
    assert small_mask(popup['text'])==image_ink(im,x,y,len(popup['text'])*8,8),popup['text']
    popups+=1
print(f'Exact ink matches: {pages} dialogue pages, {choices} choice captures, {popups} level-up popups.')
