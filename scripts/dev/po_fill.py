"""PO dosyasındaki boş çevirileri JSON'dan doldurur, başlığı düzeltir, eksikleri listeler.

Kullanım: python po_fill.py <django.po> [ceviriler.json]
"""
import json
import pathlib
import sys

import polib

po = polib.pofile(sys.argv[1], wrapwidth=79)
po.metadata['Language'] = 'tr'
po.metadata['Content-Type'] = 'text/plain; charset=UTF-8'
po.metadata_is_fuzzy = []
for entry in [e for e in po if e.obsolete]:
    po.remove(entry)

if len(sys.argv) > 2:
    translations = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding='utf-8'))
    for entry in po:
        if entry.msgid in translations:
            entry.msgstr = translations[entry.msgid]
            if 'fuzzy' in entry.flags:
                entry.flags.remove('fuzzy')

po.save()
missing = [e.msgid for e in po if not e.msgstr and not e.obsolete]
fuzzy = [e.msgid for e in po if 'fuzzy' in e.flags]
obsolete = [e.msgid for e in po if e.obsolete]
print('bos:', missing or 'yok')
print('fuzzy:', fuzzy or 'yok')
print('obsolete:', obsolete or 'yok')
