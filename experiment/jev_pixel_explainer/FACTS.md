# Jev typed decision: interface and application policy

This English pixel-video explains the **public request/response interface and application routing policy**, not the undisclosed neural architecture. It uses offline artificial values. The model was not run; there were no API calls.

## Sources inspected (2026-09-27)

- TypeSafe introduction: https://docs.typesafe.ai/introduction
- TypeSafe Choice: https://docs.typesafe.ai/primitives/choice
- Local execution evidence: `../jev_practice/results/jevfire.json`
- Local limitations: `../jev_practice/README.md`

## Claims and numbers displayed

| Display | Source and interpretation |
| --- | --- |
| `state + questions` | Official Choice request structure: state, model and questions; this film simplifies the on-screen map. |
| `Choice`, `choice`, probabilities | Official Choice response structure. A Choice selects from a defined set and returns a distribution. |
| `TYPED DATA, NOT GENERATED PROSE` | Official introduction describes typed results without text generation. This is a public interface property, not a reconstruction of the closed model internals. |
| `billing`, `technical`, `unknown` | Local fixture `request.schema.route.choices`. For the interface schematic these labels are placed in a Choice question. This is illustrative, not a captured TypeSafe API call. |
| `3 OPTIONS` | Count of those three local fixture labels, computed in `prep.py`. |
| `DOUBLE / CHARGED / REFUND?` | English paraphrase of local synthetic support-ticket context. No real customer data. |
| `0.82`, `0.12`, `0.06` | Exact artificial scores from record 0. No inference or accuracy claim. |
| `0.36`, `0.34`, `0.30` | Exact artificial scores from record 1. A second score fixture for the same synthetic schema. |
| `0.70` | Local fixture `request.min_probability`, an example application policy; not a recommended production cutoff. |
| `0.82 >= 0.70` / route to billing | Computed argmax and comparison in `prep.py`; matches upstream decoder output record 0. |
| `0.36 < 0.70` / human review | Computed comparison; matches upstream decoder abstention record 1. The human-review route is the illustrative application response to abstention. |
| `p(max)` | The largest candidate probability. **Not** TypeSafe's independent `confidence` field, which documentation describes as derived from distribution shape. |

The model panel is deliberately an interface box with no invented encoder, attention, or parallel-decoding internals. The API output is represented by precomputed fixtures and marked `ILLUSTRATIVE SCORES` and `THE MODEL WAS NOT RUN` throughout. The second fixture does not claim that changing text would yield the shown distribution.

## Storyboard / timings

| Seconds | Stage | Visible transformation |
| --- | --- | --- |
| 0–4 | STATE | Synthetic ticket words fill the persistent state module. |
| 4–8 | TYPE | A Choice question receives three explicit options. |
| 8–12 | ASK | State and question travel to the public Jev interface. |
| 12–16 | ANSWER | Offline fixture A fills typed answer and probability bars. |
| 16–21 | GATE | The application compares 0.82 with 0.70; route to billing. |
| 21–26 | CHECK | Fixture B changes the bars to 0.36 / 0.34 / 0.30. |
| 26–31 | HOLD | The same policy rejects 0.36; activate human-review branch. |
| 31–36 | RECAP | Preserve both outcomes and highlight the input-to-action map. |

Timing, native canvas 480×270, ×4 scale, 1920×1080 output, 60 fps and 36 s length are authoring parameters from the pixel-video v2 style, not model measurements. The output is silent.

## Reproduce / verify

Use Python with numpy, Pillow, imageio-ffmpeg, and local `.vendor/opencv-python-headless`.

```powershell
python -X utf8 prep.py
$env:PYTHONPATH=(Resolve-Path .vendor).Path
python -X utf8 C:/Users/YuTao/.codex/skills/pixel-video/pxv stills scene.py --times 1,5.5,9.5,14.5,19.5,24,29,34
python -X utf8 C:/Users/YuTao/.codex/skills/pixel-video/pxv check scene.py
python -X utf8 C:/Users/YuTao/.codex/skills/pixel-video/pxv still scene.py --t 19.5 --full
python -X utf8 render_windows.py
python -X utf8 C:/Users/YuTao/.codex/skills/pixel-video/pxv cover scene.py --t 19.5 --only 16x9 --title "JEV: Typed Decisions" --byline "TypeSafe docs; illustrative scores; model not run"
```

The bundled pxv renderer hard-codes Unix `fork`, so `render_windows.py` uses the same pixelkit scene/frame renderer with a bounded Windows thread executor, the installed imageio FFmpeg binary, full decode and frame verification. No skill files are changed.
