"""Check the NPC-buffer overflow regression with the required clean source ROM."""
from pathlib import Path
import copy,json,sys
from script_codec import localize_script

root=Path(__file__).resolve().parent
source=Path(sys.argv[1]).read_bytes()
manifest=json.loads((root/'cargo_road_translations.json').read_text())
_,_,report,_=localize_script(source,manifest)
assert len(report['text_buffer_limits_checked'])==4
bad=copy.deepcopy(manifest)
records={record['id']:record for record in bad['strings']}
# Both lines fit independently, but the original NPC renderer truncates their
# combined text. This is the exact layout failure found during the play check.
records['cargo_road_line_004']['english']='Ittan-momen: All this cargo'
records['cargo_road_line_005']['english']='is mine! Giii!'
try:
    localize_script(source,bad)
except AssertionError as error:
    assert 'shared NPC text buffer' in str(error),error
else:
    raise AssertionError('The overlong NPC intro was accepted')
print('NPC buffer limits: valid intro accepted; overflow regression rejected.')
