"""Regression tests for cleanup failures that previously passed silently."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from check import check
from src.content import CONTENT
from src.schema import validate_content

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('publisher', ROOT/'publish-root.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


class Safeguards(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)/'site'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        self.addCleanup(self.temp.cleanup)

    def test_missing_legacy_stylesheet_fails(self):
        (self.root/'dist/legacy/style.css').unlink()
        with self.assertRaisesRegex(ValueError, 'legacy/.*missing target style.css'):
            check(self.root/'dist')

    def test_missing_css_font_fails(self):
        (self.root/'dist/assets/montserrat-600.ttf').unlink()
        with self.assertRaisesRegex(ValueError, 'styles.css: missing target /assets/montserrat-600.ttf'):
            check(self.root/'dist')

    def test_legacy_relative_links_and_external_urls(self):
        check(self.root/'dist')

    def test_broken_privacy_redirect_fails(self):
        path = self.root/'dist/privacy.html'
        path.write_text(path.read_text().replace('/en/privacy/', '/en/missing/'))
        with self.assertRaisesRegex(ValueError, 'privacy.html: missing target'):
            check(self.root/'dist')

    def test_unowned_published_page_is_never_deleted(self):
        path = self.root/'en/obsolete/index.html'
        path.parent.mkdir(); path.write_text('Unowned')
        for options in ({'check': True}, {}, {'dry_run': True}):
            with self.assertRaisesRegex(ValueError, 'Unowned output'):
                publisher.publish(self.root, **options)
        self.assertEqual(path.read_text(), 'Unowned')

    def test_retirement_dry_run_and_preserved_configuration(self):
        path = self.root/'dist/en/about/index.html'
        path.unlink()
        before = {p: p.read_bytes() for p in [self.root/'CNAME', self.root/'legacy/index.html', self.root/'build.py']}
        with self.assertRaisesRegex(ValueError, 'manifest is stale'):
            publisher.publish(self.root, check=True)
        publisher.publish(self.root, dry_run=True)
        self.assertTrue((self.root/'en/about/index.html').exists())
        publisher.publish(self.root)
        self.assertFalse((self.root/'en/about/index.html').exists())
        for p, content in before.items():
            self.assertEqual(p.read_bytes(), content)
        publisher.publish(self.root, check=True)

    def test_modified_retired_file_blocks_all_mutation(self):
        (self.root/'dist/en/about/index.html').unlink()
        path = self.root/'en/about/index.html'; path.write_text('Owner edit')
        manifest = (self.root/'generated-files.json').read_bytes()
        with self.assertRaisesRegex(ValueError, 'refusing deletion'):
            publisher.publish(self.root)
        self.assertEqual(path.read_text(), 'Owner edit')
        self.assertEqual((self.root/'generated-files.json').read_bytes(), manifest)

    def test_manifest_cannot_claim_maintained_files_or_traverse(self):
        manifest = self.root/'generated-files.json'
        original = json.loads(manifest.read_text())
        for name in ['CNAME', 'src/content.py', '../outside', '/tmp/outside', 'legacy/index.html']:
            manifest.write_text(json.dumps({**original, name: 'bogus'}))
            with self.assertRaisesRegex(ValueError, 'Unmanaged manifest path'):
                publisher.publish(self.root)

    def test_output_symlink_is_rejected(self):
        path = self.root/'en/about/index.html'; path.unlink()
        path.symlink_to(self.root/'CNAME')
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            publisher.publish(self.root)

    def test_missing_nojekyll_fails(self):
        (self.root/'.nojekyll').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing .nojekyll'):
            publisher.publish(self.root, check=True)

    def test_locale_category_mismatch_fails(self):
        content = json.loads(json.dumps(CONTENT))
        del content['fr']['categories']['9']
        with self.assertRaisesRegex(ValueError, 'category IDs'):
            validate_content(content)

    def test_new_multidigit_category_is_valid(self):
        content = json.loads(json.dumps(CONTENT))
        for locale in content.values():
            locale['categories']['10'] = 'Additional inquiry'
        validate_content(content)

    def test_every_solution_category_exists(self):
        content = json.loads(json.dumps(CONTENT))
        content['en']['solutions'][0]['category'] = 99
        with self.assertRaisesRegex(ValueError, 'unknown category'):
            validate_content(content)


if __name__ == '__main__':
    unittest.main()
