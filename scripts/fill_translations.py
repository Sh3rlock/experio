#!/usr/bin/env python3
"""Fill Hungarian and Romanian django.po msgstr entries using polib."""

from pathlib import Path

import polib

from fill_translations_data import HU, RO

BASE = Path(__file__).resolve().parent.parent / 'locale'


def fill(lang, mapping):
    po_path = BASE / lang / 'LC_MESSAGES' / 'django.po'
    po = polib.pofile(str(po_path))
    po.metadata['Language'] = lang
    for entry in po:
        if not entry.msgid:
            continue
        if entry.msgid in mapping:
            entry.msgstr = mapping[entry.msgid]
        if entry.msgstr and 'fuzzy' in entry.flags:
            entry.flags = [flag for flag in entry.flags if flag != 'fuzzy']
    po.save(str(po_path))
    filled = sum(1 for e in po if e.msgid and e.msgstr)
    total = sum(1 for e in po if e.msgid)
    print(f'{lang}: {filled}/{total} translated')


def main():
    fill('hu', HU)
    fill('ro', RO)


if __name__ == '__main__':
    main()
