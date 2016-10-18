#!/usr/bin/env python

# Take cross-product of tokens and MeSH tree numbers in the output of
# extractTIABs.py (from https://github.com/spyysalo/pubmed)

# Expects input files to match the format output by running
#
#     python extractTIABs.py -mt -ss -tt FILE.xml.gz
#
# i.e. first one or more lines containing tokenized text, then an
# empty line, and finally a line with the format
#
#    MeSH Terms:    NUMBER (TEXT)    NUMBER (TEXT) ...
#
# Where NUMBER is a MeSH tree number, TEXT is the corresponding text of
# the MeSH term, and "MeSH Terms:" is a literal string.

from __future__ import print_function

import io
import sys
import re

MESH_LINE_MARKER = 'MeSH Terms:'
MESH_ITEM_RE = re.compile(r'^(\S+) \((.*)\)\s*$')


class FormatError(Exception):
    pass


def parse_mesh(line):
    """Parse "MeSH Terms:" line in extractTIABs.py output, return list
    of MeSH tree numbers."""
    assert line.startswith(MESH_LINE_MARKER)
    line = line[len(MESH_LINE_MARKER):].strip()
    treenums = []
    for item in line.split('\t'):
        item = item.strip()
        if not item:
            continue
        m = MESH_ITEM_RE.match(item)
        if not m:
            raise FormatError('failed to parse: {}'.format(item))
        treenums.append(m.group(1))
    return treenums


def parse(text):
    """Parse output of extractTIABs.py, return (sentences, MeSH terms)."""
    lines = text.split('\n')
    sentences = []
    for ln, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith(MESH_LINE_MARKER):
            break
        sentences.append(line.split())
    while ln < len(lines) and not lines[ln].strip():
        ln += 1
    if ln >= len(lines) or not lines[ln].startswith(MESH_LINE_MARKER):
        raise FormatError('missing MeSH marker')
    terms = parse_mesh(lines[ln])
    if any(l for l in lines[ln+1:] if l.strip()):
        raise FormatError('extra lines after MeSH: {}'.format(lines[ln+1:]))
    return sentences, terms
    

def process(fn):
    with io.open(fn, encoding='utf-8') as f:
        text = f.read()
    sentences, terms = parse(text)
    tokens = [t for s in sentences for t in s]
    for term in terms:
        for token in tokens:
            print('{{{}}}\t{}'.format(term, token.encode('utf-8')))


def main(argv):
    if len(argv) < 2:
        print('Usage: {} FILE [FILE [...]]'.format(__file__), file=sys.stderr)
        return 1

    for fn in argv[1:]:
        process(fn)
    
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
