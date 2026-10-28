---
name: figures
description: Use when animating stick-figure explainer scenes.
version: 0.1.0
license: MIT
metadata:
  tags: [animation, svg, video, stick-figure, explainer]
  repo: https://github.com/cherifya/figures
---

# figures: stick figures that act

Write short JSON scripts and the `figures` engine turns them into expressive stick-figure animation. You get a real skeletal rig, springy motion, planted-feet walks, breathing and blinking, eye contact, blended faces and a hand-drawn ink look. Renders go to SVG, MP4 or GIF.

## When to Use

- Explainer vignettes, lesson clips, story beats or social videos built from simple characters.
- Animating a short dialogue or a cause-and-effect scene in a few seconds of screen time.
- Any time you would otherwise draw stick figures by hand or settle for static frames.

Skip it for photoreal or detailed character art. This is a line-drawing engine.

## Setup

```bash
git clone https://github.com/cherifya/figures && cd figures
node tests/smoke.js                          # sanity check (Node only)
pip install playwright && playwright install chromium   # for video/stills
# plus ffmpeg on PATH
```

Install this skill by copying `skills/figures/` into your agent's skills folder, for example:
- Claude Code: `~/.claude/skills/figures/`
- Hermes: `~/.hermes/skills/figures/`

All paths below are relative to the repo root.

## Workflow

1. **Plan beats first.** Write one line per beat: who does what, then who reacts. Aim for 2 to 4 beats per 10 seconds. Each beat gets one clear gesture plus one reaction 0.2 to 0.4 s later. Hold the final tableau for at least 0.8 s.
2. **Write the spec.** Start from `examples/hello.json`. Read `skills/figures/references/spec.md` for the full vocabulary.
   - Keys are sparse; unchanged fields carry forward.
   - A standing hip sits at `y = ground - 53 * s`.
   - Put `move: "walk"` or `"run"` on the key where the walk *arrives*.
3. **Check the spec.**
   ```bash
   python3 skills/figures/scripts/check_spec.py my.json
   ```
   It catches unknown poses, expressions, looks, items and fx; unsorted keys; missing start fields; actors off canvas; bubbles over labels or heads; and actors standing on top of each other. Fix every ERROR. Read the WARNs.
4. **Render stills and look at them.**
   ```bash
   python3 tools/render.py my.json qa/ --stills 1.0 2.5 4.0 ...
   ```
   Pick one still per beat, mid-gesture. With a vision-capable agent, open each PNG. Check that the faces read correctly, that bubbles and labels don't collide, that nothing is cropped at the edges and that the legs look right mid-walk.
5. **Preview live (optional).** Run `python3 -m http.server` (as a background process) and open `/tools/player.html`. It has scrub, 0.25× speed and Load JSON.
6. **Render.**
   ```bash
   python3 tools/render.py my.json out.mp4 --workers 4
   python3 tools/render.py my.json out.gif --size 1350x600
   ```
   Each worker is a headless browser rendering its own chunk of frames. About 4 workers is the sweet spot on a laptop.

## Using the engine directly

- `FIGURES.svg(spec, t)` returns an SVG string for time `t` in seconds. Use it as a browser global (`<script src="src/figures.js">`) or in Node (`require('./src/figures.js')`).
- `FIGURES.POSES` and `FIGURES.EXPRESSIONS` list the vocabulary.
- Every frame is a pure function of `(spec, t)`. You can render any frame in any order, split a video into chunks across machines, or seek a player instantly, and you get identical output each time.

## What the engine does for you (don't script it)

- **Motion:**
  - pose changes spring in with slight overshoot; big arm moves wind up first and squash and stretch;
  - walk and run cycles are driven by distance, so feet never skate; the body bobs, the arms swing and a dust puff marks the stop;
  - turnarounds animate when `face` flips.
- **Idle life:** breathing, sway, blinks, gaze toward the nearest character and a small head tilt.
- **Follow-through:** hair, hats, ties and robes lag behind motion.
- **Faces:** expressions blend over 0.22 s. Emotion marks appear on their own:
  - `surprised`: shock lines;
  - `angry`: an anger mark;
  - `worried` or `cold`: a sweat drop;
  - `laughing`: laugh lines and a bounce.
- **Feel:** `cheer` combined with `happy` or `laughing` makes the figure hop. Figures cast ground shadows, ink lines boil 12 times a second, and the camera drifts gently.

So don't add manual blink or fidget keys, bounce keyframes for walking, or extra sweat-drop fx. Spend your keys on acting beats instead.

## Pitfalls

- **Bubbles.** Put them beside and above the speaker's head (y about 122 for `s` 1.3 on a 400-high canvas), never over the label band. `tail: -1` points down-left, `1` down-right.
- **Spacing.** A handshake needs partners about 100 px apart, hip to hip. Anything else needs at least 110 px, or limbs tangle.
- **Seated poses** (`sitting`, `sit_*`) keep seated legs. To stand up, change `y` back to the standing hip in the same key.
- **Waving.** `wiggle: {p, a}` waves the right forearm until a later key sets `wiggle: null`. Without the null it waves forever.
- **Turning.** `face` flips are animated. Don't flip it on the same key as a long walk, or the figure moonwalks for 0.2 s.
- **Edges.** Keep important props more than 40 px from the canvas edges; the camera drift zooms in slightly.
- **Determinism.** If you extend the engine, keep frames a pure function of `t`. Use seeded noise (`hsh`, `nz`) and closed-form springs, never `Math.random()` or state carried between calls. Otherwise parallel renders won't match.
- **ffmpeg filters.** Durations need a leading zero (`d=0.3`), and reusing one audio input in two `atrim`s needs `asplit`.

## Files

- `references/spec.md`: the full spec reference (poses, expressions, looks, items, fx, keyframing).
- `references/acting.md`: beat patterns that read well: entrance, greeting, reveal, argument, triumph, defeat.
- `scripts/check_spec.py`: a static linter for specs. Standard library only; run with `--strict` to fail on warnings.
