import sys
sys.path.insert(0,'analysis/v08');from play_dialogue import *
g=Game(ROM)
for selected in [0,1]:
 g.load(ROOT/'elder-report-final-menu.state')
 if selected:press(g,128,30)
 r=observe(g,f'elder-warning-selected-{selected}',True);assert r['selected']==selected and r['kind']=='choice'
 press(g,1);r=drain(g,f'elder-warning-{selected}');assert r is None
 g.save(ROOT/f'elder-warning-done-{selected}.state')
g.close()
