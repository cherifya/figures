#!/usr/bin/env python3
"""Render a figures spec to MP4 (or GIF) with K parallel headless browsers.

Every frame is a pure function of time, so the frame range is split into K chunks rendered at the same time,
then encoded in one ffmpeg pass (Apple VideoToolbox when available, else libx264).

usage:
  python3 render.py scene.json out.mp4 [--workers 4] [--fps 30] [--size 1920x1080]
  python3 render.py scene.json out.gif [--size 1350x600]
  python3 render.py scene.json stills/ --stills 1.0 2.5 4.0     # PNG stills for review

needs: pip install playwright && playwright install chromium; ffmpeg on PATH.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile, time
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = 'file://' + os.path.join(HERE, 'frame.html')


def _engine():
    """$FIGURES_JS if set, else figures.js next to this script (installed skill), else ../src/figures.js (repo checkout)."""
    for c in (os.environ.get('FIGURES_JS'), os.path.join(HERE, 'figures.js'), os.path.join(HERE, '..', 'src', 'figures.js')):
        if c and os.path.exists(c):
            return os.path.abspath(c)
    sys.exit('figures.js not found: set FIGURES_JS=/path/to/figures.js')


def _open(p, spec, W, H):
    b = p.chromium.launch(args=['--allow-file-access-from-files'])
    pg = b.new_page(viewport={'width': W, 'height': H})
    pg.goto(PAGE)
    pg.add_script_tag(path=_engine())
    pg.evaluate('([s,w,h])=>init(s,w,h)', [spec, W, H])
    pg.wait_for_function('window.READY===true')
    return b, pg


def _chunk(args):
    spec, W, H, fps, i0, i1, outdir = args
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b, pg = _open(p, spec, W, H)
        for i in range(i0, i1):
            pg.evaluate(f'render({i / fps})')
            with open(os.path.join(outdir, f'{i:06d}.jpg'), 'wb') as f:
                f.write(pg.screenshot(type='jpeg', quality=92))
        b.close()
    return i1 - i0


def _encoder():
    enc = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], capture_output=True, text=True).stdout
    return ['-c:v', 'h264_videotoolbox', '-b:v', '8M'] if 'h264_videotoolbox' in enc else ['-c:v', 'libx264', '-preset', 'medium', '-crf', '20']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec'); ap.add_argument('out')
    ap.add_argument('--workers', type=int, default=4); ap.add_argument('--fps', type=int, default=30)
    ap.add_argument('--size', default='1920x1080'); ap.add_argument('--duration', type=float)
    ap.add_argument('--gif', action='store_true'); ap.add_argument('--stills', type=float, nargs='*')
    a = ap.parse_args()
    spec = json.load(open(a.spec)); W, H = (int(x) for x in a.size.split('x'))
    if a.stills is not None:
        from playwright.sync_api import sync_playwright
        os.makedirs(a.out, exist_ok=True)
        with sync_playwright() as p:
            b, pg = _open(p, spec, W, H)
            for t in a.stills:
                pg.evaluate(f'render({t})'); pg.screenshot(path=os.path.join(a.out, f'still_{t:06.2f}.png'))
            b.close()
        print('stills ->', a.out); return
    dur = a.duration or spec.get('duration')
    if not dur: sys.exit('spec has no "duration"; pass --duration')
    n = int(round(dur * a.fps)); K = max(1, min(a.workers, n))
    tmp = tempfile.mkdtemp(prefix='figures_')
    cuts = [round(n * k / K) for k in range(K + 1)]
    t0 = time.time()
    with ProcessPoolExecutor(K) as ex:
        done = sum(ex.map(_chunk, [(spec, W, H, a.fps, cuts[k], cuts[k + 1], tmp) for k in range(K)]))
    cap = time.time() - t0
    src = ['ffmpeg', '-loglevel', 'error', '-y', '-framerate', str(a.fps), '-i', os.path.join(tmp, '%06d.jpg')]
    if a.gif or a.out.endswith('.gif'):
        vf = 'fps=15,scale=720:-1:flags=lanczos,split[x][y];[x]palettegen=max_colors=96[p];[y][p]paletteuse=dither=bayer:bayer_scale=4'
        subprocess.run(src + ['-vf', vf, a.out], check=True)
    else:
        subprocess.run(src + _encoder() + ['-pix_fmt', 'yuv420p', '-movflags', '+faststart', a.out], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(json.dumps({'out': a.out, 'frames': done, 'workers': K, 'capture_fps': round(done / cap, 1), 'total_s': round(time.time() - t0, 1)}))


if __name__ == '__main__':
    main()
