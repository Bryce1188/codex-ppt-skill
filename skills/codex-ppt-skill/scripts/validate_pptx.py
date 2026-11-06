#!/usr/bin/env python3
"""Read-only structural PPTX QA. Standard library only; not a visual fit test."""
from __future__ import annotations
import argparse
import json
import posixpath
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {'p':'http://schemas.openxmlformats.org/presentationml/2006/main', 'a':'http://schemas.openxmlformats.org/drawingml/2006/main', 'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships', 'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}

def rels(z, part):
    relpath = posixpath.join(posixpath.dirname(part), '_rels', posixpath.basename(part) + '.rels')
    if relpath not in z.namelist():
        return {}
    result = {}
    for el in ET.fromstring(z.read(relpath)):
        target = el.attrib['Target']
        external = el.attrib.get('TargetMode') == 'External'
        resolved = target if external else posixpath.normpath(posixpath.join(posixpath.dirname(part), target)).lstrip('/')
        result[el.attrib['Id']] = {'target':resolved, 'type':el.attrib['Type'], 'external':external}
    return result

def inspect(path, expected=None, text_pages=(), chart_pages=(), table_pages=(), notes_pages=()):
    report = {'file': str(Path(path).resolve()), 'errors': [], 'warnings': [], 'slides': [], 'limitations': ['No visual inspection, text fitting, group-coordinate resolution, chart arithmetic, or application compatibility is proved by this check.']}
    errors, warnings = report['errors'], report['warnings']
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        for required in ('[Content_Types].xml', '_rels/.rels', 'ppt/presentation.xml', 'ppt/_rels/presentation.xml.rels'):
            if required not in names:
                errors.append(f'Missing required part: {required}')
        if errors:
            report['passed'] = False
            return report
        for name in sorted(names):
            if name.endswith(('.xml', '.rels')):
                try: ET.fromstring(z.read(name))
                except ET.ParseError as exc: errors.append(f'Malformed XML {name}: {exc}')
            if name.endswith('.rels'):
                owner_dir, rel_name = posixpath.split(name)
                owner = posixpath.join(posixpath.dirname(owner_dir), rel_name[:-5])
                for relation in rels(z, owner).values():
                    if not relation['external'] and relation['target'] not in names:
                        errors.append(f'Broken relationship: {name} -> {relation["target"]}')
        root = ET.fromstring(z.read('ppt/presentation.xml'))
        size = root.find('p:sldSz', NS)
        width, height = int(size.attrib['cx']), int(size.attrib['cy'])
        report['slide_size_emu'] = [width, height]
        links = rels(z, 'ppt/presentation.xml')
        slides = root.findall('p:sldIdLst/p:sldId', NS)
        if expected is not None and expected != len(slides): errors.append(f'Expected {expected} slides; found {len(slides)}')
        for pages in (text_pages, chart_pages, table_pages, notes_pages):
            for n in pages:
                if n < 1 or n > len(slides): errors.append(f'Required slide {n} is out of range')
        for n, sid in enumerate(slides, 1):
            relation = links.get(sid.attrib['{' + NS['r'] + '}id'])
            if not relation or relation['target'] not in names:
                errors.append(f'Slide {n} has no usable relationship')
                continue
            part = relation['target']
            slide = ET.fromstring(z.read(part))
            texts = [x.text or '' for x in slide.findall('.//a:t', NS)]
            chart_count = len(slide.findall('.//c:chart', NS))
            table_count = len(slide.findall('.//a:tbl', NS))
            images = len(slide.findall('.//p:pic', NS))
            notes = ''
            for rel in rels(z, part).values():
                if rel['type'].endswith('/notesSlide') and rel['target'] in names:
                    nr = ET.fromstring(z.read(rel['target']))
                    bodies = nr.findall('.//p:sp', NS)
                    for body in bodies:
                        ph = body.find('p:nvSpPr/p:nvPr/p:ph', NS)
                        if ph is None or ph.attrib.get('type') == 'body':
                            notes += '\n'.join(t.text or '' for t in body.findall('.//a:t', NS))
            count = {'slide':n, 'part':part, 'text_runs':len(texts), 'text_chars':sum(map(len,texts)), 'native_charts':chart_count, 'native_tables':table_count, 'images':images, 'notes_chars':len(notes.strip())}
            report['slides'].append(count)
            for pages, present, label in ((text_pages, any(t.strip() for t in texts), 'editable text'), (chart_pages, chart_count, 'native chart'), (table_pages, table_count, 'native table'), (notes_pages, notes.strip(), 'notes')):
                if n in pages and not present: errors.append(f'Slide {n}: missing required {label}')
            if images and not texts and not chart_count and not table_count: warnings.append(f'Slide {n}: image-only content; words/data in images cannot be edited as native objects')
            if re.search(r'\b(?:lorem ipsum|TODO|TBD)\b|请输入文本|点击此处添加', '\n'.join(texts), re.I): warnings.append(f'Slide {n}: possible placeholder text; inspect context')
            tree = slide.find('p:cSld/p:spTree', NS)
            if tree is not None:
                for obj in tree:
                    if obj.tag.endswith('}grpSp'): warnings.append(f'Slide {n}: grouped object requires visual geometry check'); continue
                    xf = obj.find('p:spPr/a:xfrm', NS)
                    if xf is None: xf = obj.find('p:xfrm', NS)
                    if xf is None: continue
                    off, ext = xf.find('a:off', NS), xf.find('a:ext', NS)
                    if off is None or ext is None: continue
                    x, y, w, h = (int(off.attrib['x']), int(off.attrib['y']), int(ext.attrib['cx']), int(ext.attrib['cy']))
                    if x < -12700 or y < -12700 or x+w > width+12700 or y+h > height+12700: warnings.append(f'Slide {n}: object may exceed slide bounds; inspect cropping/rotation intent')
    report['passed'] = not errors
    return report

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pptx')
    parser.add_argument('--expected-slides', type=int)
    parser.add_argument('--report')
    for field in ('text','chart','table','notes'):
        parser.add_argument(f'--require-{field}', type=int, nargs='*', default=[])
    args = parser.parse_args()
    try:
        report = inspect(args.pptx, args.expected_slides, args.require_text, args.require_chart, args.require_table, args.require_notes)
    except (OSError, zipfile.BadZipFile, ET.ParseError, KeyError, TypeError, ValueError) as exc:
        report = {'file':args.pptx, 'passed':False, 'errors':[str(exc)], 'warnings':[]}
    if args.report:
        out = Path(args.report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['passed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
