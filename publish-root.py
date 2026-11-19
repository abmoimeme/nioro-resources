#!/usr/bin/env python3
"""Publish generated files safely; never delete unowned or edited files."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parent
MANIFEST = 'generated-files.json'
DIRECTORIES = {'en', 'fr', 'assets'}
FILES = {'index.html', '404.html', 'privacy.html', 'styles.css', 'app.js', 'config.js', 'robots.txt', 'sitemap.xml', '_headers'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_target(root, name):
    path = PurePosixPath(name)
    if str(path) != name or path.is_absolute() or '..' in path.parts or not (
        name in FILES or len(path.parts) > 1 and path.parts[0] in DIRECTORIES
    ):
        raise ValueError(f'Unmanaged manifest path: {name}')
    target = root / name
    current = target
    while current != root:
        if current.is_symlink():
            raise ValueError(f'Symlink in output path: {name}')
        current = current.parent
    return target


def publish(root=ROOT, check=False, dry_run=False):
    dist = root / 'dist'
    files = [p for p in dist.rglob('*') if p.is_file()]
    if not files:
        raise ValueError('Run build.py first')
    # legacy/ is maintained source and copied into dist, never deletion-owned.
    generated = {p.relative_to(dist).as_posix(): digest(p) for p in files
                 if p.relative_to(dist).parts[0] != 'legacy'}
    manifest_path = root / MANIFEST
    previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for name in previous.keys() | generated.keys():
        safe_target(root, name)
    present = {p.relative_to(root).as_posix() for directory in DIRECTORIES
               for p in (root/directory).rglob('*') if p.is_file()}
    unknown = present - previous.keys() - generated.keys()
    if unknown:
        raise ValueError('Unowned output files; review explicitly: ' + ', '.join(sorted(unknown)))
    stale = previous.keys() - generated.keys()
    # Check everything before any mutation.
    for name in stale:
        target = safe_target(root, name)
        if target.exists() and digest(target) != previous[name]:
            raise ValueError(f'Retired output was edited; refusing deletion: {name}')
    for p in files:
        if p.relative_to(dist).parts[0] == 'legacy':
            target = root/p.relative_to(dist)
            if not target.is_file() or target.read_bytes() != p.read_bytes():
                raise ValueError(f'Legacy source/output mismatch: {p.relative_to(dist)}')
    if check:
        if previous != generated:
            raise ValueError('Generated manifest is stale: run publish-root.py')
        for name, expected in generated.items():
            target = safe_target(root, name)
            if not target.is_file() or digest(target) != expected:
                raise ValueError(f'Published file is stale or missing: {name}')
        if not (root/'.nojekyll').is_file():
            raise ValueError('Missing .nojekyll')
        print('PASS: published files and generated manifest match the build.')
        return
    for name in sorted(stale):
        print('Remove retired generated file:', name)
    if dry_run:
        print(f'Dry run: {len(generated)} generated files; {len(stale)} retired files; no changes.')
        return
    for name in stale:
        safe_target(root, name).unlink(missing_ok=True)
    for name in generated:
        target = safe_target(root, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dist/name, target)
    manifest_path.write_text(json.dumps(generated, indent=2, sort_keys=True)+'\n')
    (root/'.nojekyll').touch()
    print(f'Published {len(generated)} generated files; preserved maintained source and configuration.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    publish(check=args.check, dry_run=args.dry_run)
