#!/usr/bin/env python3
"""Copy the tested dist output to the existing GitHub Pages repository root."""
from pathlib import Path
import shutil,sys
root=Path(__file__).resolve().parent
files=[p for p in (root/'dist').rglob('*') if p.is_file()]
assert files, 'Run python3 build.py first.'
check='--check' in sys.argv
for p in files:
 target=root/p.relative_to(root/'dist')
 if check:
  assert target.exists() and target.read_bytes()==p.read_bytes(), f'Rebuild and run publish-root.py: {target}'
 else:
  target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
if not check:(root/'.nojekyll').touch()
print('Published root matches build.' if check else 'Updated branch-root website files.')
