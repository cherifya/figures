#!/usr/bin/env python3
"""Copy the engine, renderer and examples into skills/figures/ so the skill works on its own
when `npx skills add cherifya/figures` copies only that folder.

usage: python3 tools/sync_skill.py          # copy
       python3 tools/sync_skill.py --check  # exit 1 if the skill copy is stale (used by the tests)
"""
import filecmp, glob, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, 'skills', 'figures')
PAIRS = [('src/figures.js', 'scripts/figures.js'), ('tools/render.py', 'scripts/render.py'),
         ('tools/frame.html', 'scripts/frame.html'), ('LICENSE', 'LICENSE')]
PAIRS += [(os.path.relpath(p, ROOT), 'assets/examples/' + os.path.basename(p)) for p in sorted(glob.glob(os.path.join(ROOT, 'examples', '*.json')))]


def main():
    check = '--check' in sys.argv
    stale = []
    for a, b in PAIRS:
        src, dst = os.path.join(ROOT, a), os.path.join(SK, b)
        if not (os.path.exists(dst) and filecmp.cmp(src, dst, shallow=False)):
            stale.append(b)
            if not check:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
    if check and stale:
        sys.exit('skill copy is stale, run python3 tools/sync_skill.py: ' + ', '.join(stale))
    print('skill in sync' if check or not stale else 'synced: ' + ', '.join(stale))


if __name__ == '__main__':
    main()
