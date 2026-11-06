#!/usr/bin/env python3
"""Check asset provenance fields, source hashes and exact PPTX picture relationships."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import posixpath
import sys
import xml.etree.ElementTree as ET
import zipfile

NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def picture_hashes(deck):
    """Follow presentation slide order, then actual picture blips, not unused media."""
    with zipfile.ZipFile(deck) as z:
        def relations(part):
            folder, name = posixpath.split(part)
            relpart = posixpath.join(folder, '_rels', name + '.rels')
            if relpart not in z.namelist():
                return {}
            return {r.attrib['Id']: posixpath.normpath(posixpath.join(folder, r.attrib['Target'].lstrip('/'))) if not r.attrib['Target'].startswith('/') else r.attrib['Target'].lstrip('/')
                    for r in ET.fromstring(z.read(relpart)) if r.attrib.get('TargetMode') != 'External'}
        rels = relations('ppt/presentation.xml')
        root = ET.fromstring(z.read('ppt/presentation.xml'))
        slides = [rels[s.attrib['{' + NS['r'] + '}id']] for s in root.findall('p:sldIdLst/p:sldId', NS)]
        result = {}
        for number, part in enumerate(slides, 1):
            mapping = relations(part)
            tree = ET.fromstring(z.read(part))
            refs = [b.attrib.get('{' + NS['r'] + '}embed') for b in tree.findall('.//p:pic/p:blipFill/a:blip', NS)]
            result[number] = {sha(z.read(mapping[r])) for r in refs if r in mapping}
        return result


def validate(manifest_path: Path, pptx=None):
    doc = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    errors = []
    count = doc.get('slide_count')
    if type(count) is not int or count < 1:
        return {'passed': False, 'errors': ['positive integer slide_count required']}
    assets = doc.get('assets')
    if not isinstance(assets, list) or not assets:
        return {'passed': False, 'errors': ['nonempty assets required; missing assets must be reported as a gap']}
    pictures = picture_hashes(pptx) if pptx else None
    if pictures is not None and len(pictures) != count:
        errors.append('PPTX slide count differs from manifest')
    seen = set()
    for asset in assets:
        if not isinstance(asset, dict):
            errors.append('asset must be an object')
            continue
        ident = asset.get('id')
        if not isinstance(ident, str) or not ident or ident in seen:
            errors.append('asset id must be a unique nonempty string')
        else:
            seen.add(ident)
        for field in ('path', 'source', 'caption'):
            if not isinstance(asset.get(field), str) or not asset[field].strip():
                errors.append(f'{ident}: {field} required')
        if asset.get('role') not in ('evidence', 'decoration'):
            errors.append(f'{ident}: invalid role')
        if asset.get('kind') not in ('screenshot', 'source_figure', 'rendered_result', 'decoration'):
            errors.append(f'{ident}: invalid kind')
        if asset.get('kind') == 'screenshot' and not str(asset.get('capture', '')).strip():
            errors.append(f'{ident}: screenshot capture record required')
        if asset.get('role') == 'evidence' and asset.get('fit') != 'contain':
            errors.append(f'{ident}: evidence must use contain')
        pages = asset.get('slides')
        if not isinstance(pages, list) or not pages or any(type(n) is not int or n < 1 or n > count for n in pages):
            errors.append(f'{ident}: slides must refer to existing pages')
            pages = []
        try:
            source = manifest_path.parent / asset.get('path', '')
            digest = sha(source.read_bytes())
            if digest != asset.get('sha256'):
                errors.append(f'{ident}: source SHA256 mismatch')
            if pictures is not None:
                for page in pages:
                    if digest not in pictures.get(page, set()):
                        errors.append(f'{ident}: original image not referenced by a picture on slide {page}')
        except (OSError, TypeError) as exc:
            errors.append(f'{ident}: cannot read source: {exc}')
    return {'passed': not errors, 'errors': errors, 'asset_count': len(assets),
            'pptx_checked': pictures is not None,
            'scope': 'Source bytes and picture relationships only; inspect truth, position and visibility separately.'}


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--pptx', type=Path)
    args = parser.parse_args()
    try:
        report = validate(args.manifest, args.pptx)
    except (OSError, ValueError, KeyError, ET.ParseError, zipfile.BadZipFile) as exc:
        parser.exit(1, f'Asset validation failed: {exc}\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
