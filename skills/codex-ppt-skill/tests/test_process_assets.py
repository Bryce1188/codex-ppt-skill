import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


process = module('resolve_superpowers')
assets = module('validate_assets')


class ProcessTests(unittest.TestCase):
    def test_missing_uses_explicit_fallback(self):
        with tempfile.TemporaryDirectory() as folder:
            result = process.resolve(Path(folder) / 'ppt', installed_roots=[])
            self.assertFalse(result['available'])
            self.assertTrue((ROOT / result['fallback']).is_file())

    def test_explicit_missing_does_not_fall_back(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                process.resolve(ROOT, Path(folder) / 'absent')

    def test_pack_and_split_layouts(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            for name in process.NAMES:
                target = base / 'superpowers/skills' / name / 'SKILL.md'
                target.parent.mkdir(parents=True)
                target.write_text(f'---\nname: {name}\n---\nRules', encoding='utf-8')
            result = process.resolve(base / 'ppt', installed_roots=[])
            self.assertEqual(result['resolved_from'], 'sibling')
            self.assertEqual(result['missing'], [])
            split = process.resolve(base / 'other/ppt', installed_roots=[base / 'superpowers/skills'])
            self.assertEqual(split['resolved_from'], 'installed-split')
            self.assertEqual(split['skills'], result['skills'])

    def test_partial_install_reports_missing_skills(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            target = base / 'brainstorming/SKILL.md'
            target.parent.mkdir()
            target.write_text('---\nname: brainstorming\n---\nRules', encoding='utf-8')
            result = process.resolve(ROOT, explicit=base)
            self.assertEqual(result['missing'], ['writing-plans', 'verification-before-completion'])


class AssetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.data = (ROOT / 'examples/course-report/assets/cover-background.png').read_bytes()
        (self.base / 'source.png').write_bytes(self.data)
        self.doc = {'slide_count': 2, 'assets': [{'id': 'source', 'path': 'source.png',
                    'source': 'fixture only', 'role': 'evidence', 'kind': 'screenshot',
                    'capture': 'test fixture, no live capture', 'caption': 'test image',
                    'fit': 'contain', 'slides': [2], 'sha256': hashlib.sha256(self.data).hexdigest()}]}
        self.manifest = self.base / 'assets.json'
        self.deck = self.base / 'fixture.pptx'
        # Intentionally reverse slide filenames to test actual presentation order.
        p = assets.NS['p']; a = assets.NS['a']; r = assets.NS['r']
        with zipfile.ZipFile(self.deck, 'w') as z:
            z.writestr('ppt/presentation.xml', f'<p:presentation xmlns:p="{p}" xmlns:r="{r}"><p:sldIdLst><p:sldId r:id="a"/><p:sldId r:id="b"/></p:sldIdLst></p:presentation>')
            z.writestr('ppt/_rels/presentation.xml.rels', '<Relationships><Relationship Id="a" Target="slides/slide2.xml"/><Relationship Id="b" Target="slides/slide1.xml"/></Relationships>')
            z.writestr('ppt/slides/slide2.xml', f'<p:sld xmlns:p="{p}"/>')
            z.writestr('ppt/slides/slide1.xml', f'<p:sld xmlns:p="{p}" xmlns:a="{a}" xmlns:r="{r}"><p:pic><p:blipFill><a:blip r:embed="image"/></p:blipFill></p:pic></p:sld>')
            z.writestr('ppt/slides/_rels/slide1.xml.rels', '<Relationships><Relationship Id="image" Target="../media/source.png"/></Relationships>')
            z.writestr('ppt/media/source.png', self.data)

    def check(self, pptx=True):
        self.manifest.write_text(json.dumps(self.doc), encoding='utf-8')
        return assets.validate(self.manifest, self.deck if pptx else None)

    def test_original_image_on_correct_ordered_slide_passes(self):
        self.assertTrue(self.check()['passed'])

    def test_image_in_package_but_wrong_slide_fails(self):
        self.doc['assets'][0]['slides'] = [1]
        self.assertFalse(self.check()['passed'])

    def test_changed_source_bytes_fail(self):
        (self.base / 'source.png').write_bytes(b'changed')
        self.assertFalse(self.check()['passed'])

    def test_bad_page_crop_and_missing_capture_fail(self):
        asset = self.doc['assets'][0]
        asset.update(slides=[3], fit='cover', capture='')
        result = self.check()
        self.assertFalse(result['passed'])
        self.assertEqual(len(result['errors']), 3)

    def test_empty_manifest_cannot_claim_verification(self):
        self.doc['assets'] = []
        self.assertFalse(self.check()['passed'])


if __name__ == '__main__':
    unittest.main()
