"""Check that a localized item name cannot shift or overwrite item data."""
from pathlib import Path
import json,sys
from build_patch import apply_fixed_item_name,encode

root=Path(__file__).resolve().parent
source=Path(sys.argv[1]).read_bytes()
item=next(x for x in json.loads((root/'translations.json').read_text())['strings']
          if x['id']=='item_healing_medicine')
offset=int(item['offset'],16);original=bytes.fromhex(item['source_hex'])
raw=encode(item['english'])+b'\0';patched=bytearray(source)
apply_fixed_item_name(source,patched,offset,original,raw)
assert patched[:offset]==source[:offset]
assert patched[offset+len(raw):]==source[offset+len(raw):]
# A shorter, individually valid UI name must not shift the embedded effect data.
for bad in [encode('Med\x01')+b'\0',encode('HP Med!\x01')+b'\0']:
    candidate=bytearray(source)
    try:
        apply_fixed_item_name(source,candidate,offset,original,bad)
    except AssertionError as error:
        assert 'fixed item name size' in str(error),error
        assert candidate==source
    else:
        raise AssertionError('A changed item-record extent was accepted')
print('Item layout: valid name accepted; shorter and longer names rejected; item data preserved.')
