# Devpost media assets

The six PNG files were captured from the running controlled synthetic demo and normalized to 1440×960 (3:2). They contain no real accounts, private filenames, tokens, or real student information.

`learnstep-demo.mp4` is generated exclusively from those verified screenshots. It is silent, captioned, 63.20 seconds long, 1440×960, H.264/yuv420p, and contains no audio stream.

## Captions

1. Landing page, product boundary, and local service state.
2. Synthetic learner selection for Class 5 Mathematics and Class 6 Science.
3. Synthetic chapter selection with source and confidence wording.
4. Structured lesson, exact source page, and practice question.
5. Staged hint before answer reveal.
6. Deterministic feedback and non-ranking learning evidence.

## Regenerate the MP4

Use an isolated media-only environment; these packages are not application runtime dependencies.

```powershell
py -3.12 -m venv .media-venv
.\.media-venv\Scripts\python.exe -m pip install "Pillow>=10.4,<13" "imageio-ffmpeg==0.6.0"
.\.media-venv\Scripts\python.exe scripts\create_devpost_video.py
```

The generator validates source dimensions, normalizes browser captures to 3:2, adds only the documented captions, creates short crossfades, and writes `docs/media/devpost/learnstep-demo.mp4`.
