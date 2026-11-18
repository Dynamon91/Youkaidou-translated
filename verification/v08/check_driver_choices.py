import sys
sys.path.insert(0,'analysis/v08');from play_dialogue import *
g=Game(ROM)
for selected in [0,1]:
 g.load(ROOT/'driver-intro-menu.state')
 if selected:press(g,128,30)
 r=observe(g,f'driver-praise-selected-{selected}',True);assert r['kind']=='choice' and r['menu']==1 and r['selected']==selected
 press(g,1);r=drain(g,f'driver-praise-{selected}');assert r and r['menu']==2
for selected in [0,1]:
 g.load(ROOT/'driver-praise-0-menu.state')
 if selected:press(g,128,30)
 r=observe(g,f'driver-silence-selected-{selected}',True);assert r['kind']=='choice' and r['menu']==2 and r['selected']==selected
 press(g,1);r=drain(g,f'driver-silence-{selected}');assert r and r['menu']==3
for selected in [0,1]:
 g.load(ROOT/'driver-silence-0-menu.state')
 if selected:press(g,128,30)
 r=observe(g,f'driver-help-selected-{selected}',True);assert r['kind']=='choice' and r['menu']==3 and r['selected']==selected
 press(g,1);r=drain(g,f'driver-help-{selected}');assert r is None
 g.save(ROOT/f'returned-village-{selected}.state')
g.close()
