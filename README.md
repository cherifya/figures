# figures

Stick-figure animation from short JSON scripts. You say who stands where and what each character does at which second, and figures animates everything in between: the walking, the gestures, the blinking, the eye contact, and faces that change with the mood. The engine is a single JavaScript file with no dependencies. It draws SVG in the browser, and a small Python tool renders scenes to MP4 or GIF.

![Two stick figures meet, wave, shake hands and laugh at a bad joke](media/hello.gif)

## Before and after

This clip plays the same script through two engines. On the left is [stix](https://github.com/bassimeledath/stix), which figures grew out of. On the right is figures. The clip is 21 seconds, with no sound.

[![The same Law 1 scene rendered by stix and by figures](media/side_by_side.jpg)](media/side_by_side.mp4)

## How it animates

stix moves a character by sliding each joint in a straight line from one pose to the next, so arms shrink halfway through a gesture and feet skate across the floor. figures gives every character a skeleton instead.
- Bones rotate around their joints, so limbs keep their length and hands travel along arcs.
- A walk or run takes steps sized to the distance covered, so the feet stay planted. The body bobs while the arms swing.

Pose changes run on a spring, so a pointing arm overshoots a little and settles. Large gestures wind up before they go. Hair, hats, ties and robes trail behind fast moves, and turning around plays as a turn rather than a mirror flip.

Nobody freezes between keyframes. Characters breathe, sway, blink at uneven intervals and look at whoever is closest. Each face is a set of brows, eyes and a mouth that blend between 11 expressions. Some expressions bring their own marks: shock lines for surprise, a throbbing mark for anger, a sweat drop for worry.

The ink lines are redrawn with a slight wobble 12 times a second, as in hand-drawn animation. Each figure also casts a soft shadow that shrinks when it jumps.

## Install as an agent skill

`skills/figures` is an [Agent Skill](https://agentskills.io). It contains:
- the engine and the renderer;
- a linter for scene files;
- the full scene reference and timing notes for common beats;
- example scenes.

Install it with the [skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add cherifya/figures                    # current project
npx skills add cherifya/figures -g                 # every project
npx skills add cherifya/figures -a claude-code     # one agent only
```

Then describe the scene you want, for example "animate a 10 second scene where a kid teaches her dad a secret handshake." The skill has the agent:
1. plan the beats;
2. write the JSON;
3. lint it;
4. check stills from the key moments;
5. render the video.

If the CLI doesn't support your agent, copy `skills/figures/` into the agent's skills folder.

## Use it in code

In a page:

```html
<div id="stage" style="width:900px;height:400px"></div>
<script src="src/figures.js"></script>
<script>
  fetch('examples/hello.json').then(r => r.json()).then(spec => {
    const t0 = performance.now();
    (function tick(now) {
      stage.innerHTML = FIGURES.svg(spec, ((now - t0) / 1000) % spec.duration);
      requestAnimationFrame(tick);
    })(t0);
  });
</script>
```

In Node:

```js
const FIGURES = require('./src/figures.js');
const svg = FIGURES.svg(require('./examples/hello.json'), 2.5); // the scene at 2.5 seconds
```

To scrub through a scene, slow it down or load your own file, serve the repo with `python3 -m http.server` and open `http://localhost:8000/tools/player.html`.

## Render video

```bash
pip install playwright && playwright install chromium   # ffmpeg also needs to be on PATH
python3 tools/render.py examples/hello.json hello.mp4 --workers 4
python3 tools/render.py examples/hello.json hello.gif --size 1350x600
python3 tools/render.py examples/hello.json qa/ --stills 1.5 4.0 6.7
```

The renderer splits the frames across several headless browsers and encodes the result once. It uses Apple VideoToolbox when the machine has it and libx264 otherwise. A frame depends only on the scene and the time, so the slices join exactly.

On a MacBook Air (M5) at 1920×1080:
- One browser captures about 29 frames per second.
- Four browsers together capture 82 to 97.
- Building the SVG for a frame takes well under a millisecond, so almost all the time goes to screenshots.

## Writing scenes

```json
{"w": 900, "h": 400, "ground": 355, "duration": 6,
 "fx": [{"type": "bubble", "x": 240, "y": 120, "t0": 2.2, "t1": 4, "text": "Hi there", "tail": -1}],
 "actors": [
  {"label": "ADA", "s": 1.3, "keys": [
    {"t": 0, "x": -80, "y": 286, "pose": "standing", "expr": "neutral"},
    {"t": 2.0, "x": 330, "move": "walk", "expr": "happy"},
    {"t": 2.4, "pose": "waving", "wiggle": {"p": 0.4, "a": 6}}]}]}
```

Ada walks in from the left, smiles and waves while her speech bubble is up.

Fields you leave out of a key carry over from the one before.
- [The scene reference](skills/figures/references/spec.md) lists the 40 poses, 11 expressions, costumes, props and effects.
- [acting.md](skills/figures/references/acting.md) gives timings for greetings, reveals, arguments and other common beats.

Before rendering, run `python3 skills/figures/scripts/check_spec.py scene.json`. It catches typos in pose names, characters floating off the ground, and speech bubbles that cover someone's name.

## Development

```bash
npm test                      # renders every frame of the examples and lints them
python3 tools/sync_skill.py   # run after editing src/, tools/ or examples/
```

The skill folder carries its own copy of the engine, renderer and examples, so `npx skills add` works without the rest of the repo. The test fails if those copies fall out of date.

## Credits

figures started as a rewrite of [stix](https://github.com/bassimeledath/stix) by Bassime Ledath (MIT) and keeps its pose library, props and effects. The skeleton, motion, faces and parallel renderer are new. The mirror and court examples come from a stick-figure series about power and history.

## License

MIT. See [LICENSE](LICENSE).
