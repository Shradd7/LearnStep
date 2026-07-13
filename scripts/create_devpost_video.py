"""Create the silent, captioned LearnStep Devpost demo from verified screenshots.

This is a portfolio-media utility, not an application runtime dependency. It
requires Pillow and imageio-ffmpeg. Run it from the repository root.
"""

from __future__ import annotations

import argparse
import importlib
import subprocess
import tempfile
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, cast

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1440
HEIGHT = 960
FPS = 30
TRANSITION_SECONDS = 0.8
BACKGROUND = "#f4f0e6"
INK = "#132821"
ACCENT = "#146b52"


@dataclass(frozen=True)
class Slide:
    image_name: str | None
    step: str
    caption: str
    duration_seconds: float


class ImageioFfmpegModule(Protocol):
    def get_ffmpeg_exe(self) -> str: ...


SLIDES = (
    Slide("01-landing.png", "01 · INTRO", "Upload. Learn. Ace it.", 8),
    Slide(
        "02-synthetic-learner-selection.png",
        "02 · CONTROLLED ENTRY",
        "A synthetic learner enters the controlled demo—no real child data.",
        9,
    ),
    Slide(
        "03-chapter-selection.png",
        "03 · CHOOSE A STEP",
        "Select a class-appropriate synthetic chapter with visible source confidence.",
        9,
    ),
    Slide(
        "04-source-grounded-lesson.png",
        "04 · LEARN",
        "See a structured lesson and practice question tied to source details.",
        10,
    ),
    Slide(
        "05-staged-hint.png",
        "05 · HINT FIRST",
        "Request staged support before revealing the reviewed demo answer.",
        10,
    ),
    Slide(
        "06-feedback-and-progress.png",
        "06 · FEEDBACK",
        "Receive deterministic answer feedback and non-ranking learning evidence.",
        10,
    ),
    Slide(
        None,
        "LEARNSTEP",
        "Controlled synthetic demo—privacy-first, NLP-first learning support.",
        12,
    ),
)


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def _normalize_screenshot(path: Path) -> None:
    """Preserve the full capture while fitting it to the required 3:2 canvas."""
    image = Image.open(path).convert("RGB")
    if image.size == (WIDTH, HEIGHT):
        return

    target_ratio = WIDTH / HEIGHT
    current_ratio = image.width / image.height
    if current_ratio > target_ratio:
        canvas_height = round(image.width / target_ratio)
        canvas = Image.new("RGB", (image.width, canvas_height), BACKGROUND)
        canvas.paste(image, (0, (canvas_height - image.height) // 2))
    else:
        canvas_width = round(image.height * target_ratio)
        canvas = Image.new("RGB", (canvas_width, image.height), BACKGROUND)
        canvas.paste(image, ((canvas_width - image.width) // 2, 0))

    canvas.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).save(path, format="PNG", optimize=True)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, width: int) -> str:
    approximate_chars = max(18, int(width / max(font.getlength("M"), 1)))
    lines = textwrap.wrap(text, width=approximate_chars)
    while any(draw.textlength(line, font=font) > width for line in lines):
        approximate_chars -= 1
        lines = textwrap.wrap(text, width=max(18, approximate_chars))
    return "\n".join(lines)


def _captioned_slide(source: Path, slide: Slide, output: Path) -> None:
    image = Image.open(source).convert("RGB")
    if image.size != (WIDTH, HEIGHT):
        raise ValueError(f"Expected {WIDTH}x{HEIGHT} screenshot, got {image.size}: {source}")

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((42, 710, 1398, 930), radius=22, fill=(19, 40, 33, 242))

    label_font = _font("C:/Windows/Fonts/segoeuib.ttf", 24)
    caption_font = _font("C:/Windows/Fonts/segoeui.ttf", 34)
    draw.text((82, 746), slide.step, font=label_font, fill="#8cd5bd")
    wrapped = _wrap(draw, slide.caption, caption_font, 1270)
    draw.multiline_text((82, 795), wrapped, font=caption_font, fill="white", spacing=6)

    Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB").save(
        output, format="PNG", optimize=True
    )


def _closing_slide(slide: Slide, output: Path) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    brand_font = _font("C:/Windows/Fonts/georgia.ttf", 92)
    label_font = _font("C:/Windows/Fonts/segoeuib.ttf", 26)
    body_font = _font("C:/Windows/Fonts/segoeui.ttf", 46)

    draw.ellipse((110, 120, 210, 220), fill=ACCENT)
    mark_font = _font("C:/Windows/Fonts/segoeuib.ttf", 50)
    draw.text((145, 137), "L", font=mark_font, fill="white", anchor="ma")
    draw.text((245, 116), "LearnStep", font=brand_font, fill=INK)
    draw.text((118, 320), "UPLOAD. LEARN. ACE IT.", font=label_font, fill=ACCENT)
    wrapped = _wrap(draw, slide.caption, body_font, 1160)
    draw.multiline_text((118, 390), wrapped, font=body_font, fill=INK, spacing=16)
    draw.rounded_rectangle((118, 680, 1288, 790), radius=18, fill="white", outline="#d6cfbf")
    note_font = _font("C:/Windows/Fonts/segoeui.ttf", 29)
    draw.text(
        (158, 716),
        "Synthetic accounts and content only · No educational-improvement claim",
        font=note_font,
        fill="#385149",
    )
    image.save(output, format="PNG", optimize=True)


def _ffmpeg_executable(explicit_path: str | None) -> str:
    if explicit_path:
        return explicit_path
    module = cast(
        ImageioFfmpegModule,
        importlib.import_module("imageio_ffmpeg"),
    )
    return module.get_ffmpeg_exe()


def _encode(ffmpeg: str, slide_paths: list[Path], output: Path) -> None:
    command = [ffmpeg, "-y"]
    for slide_path, slide in zip(slide_paths, SLIDES, strict=True):
        command.extend(
            [
                "-loop",
                "1",
                "-framerate",
                str(FPS),
                "-t",
                str(slide.duration_seconds),
                "-i",
                str(slide_path),
            ]
        )

    filters: list[str] = []
    for index in range(len(SLIDES)):
        filters.append(
            f"[{index}:v]fps={FPS},scale={WIDTH}:{HEIGHT},setsar=1,"
            f"format=yuv420p,settb=AVTB[v{index}]"
        )

    previous = "v0"
    elapsed = SLIDES[0].duration_seconds
    for index in range(1, len(SLIDES)):
        offset = elapsed - TRANSITION_SECONDS * index
        output_label = f"x{index}"
        filters.append(
            f"[{previous}][v{index}]xfade=transition=fade:"
            f"duration={TRANSITION_SECONDS}:offset={offset:.3f}[{output_label}]"
        )
        previous = output_label
        elapsed += SLIDES[index].duration_seconds

    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            f"[{previous}]",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-an",
            str(output),
        ]
    )
    # The executable is either an explicit local path or the packaged imageio-ffmpeg binary.
    subprocess.run(command, check=True)  # noqa: S603


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--media-dir", type=Path, default=Path("docs/media/devpost"))
    parser.add_argument("--ffmpeg", help="Optional path to an ffmpeg executable")
    args = parser.parse_args()

    media_dir = args.media_dir.resolve()
    output = media_dir / "learnstep-demo.mp4"
    media_dir.mkdir(parents=True, exist_ok=True)

    for image_name in {slide.image_name for slide in SLIDES if slide.image_name is not None}:
        _normalize_screenshot(media_dir / image_name)

    with tempfile.TemporaryDirectory(prefix="learnstep-devpost-") as temp:
        temp_dir = Path(temp)
        slide_paths: list[Path] = []
        for index, slide in enumerate(SLIDES, start=1):
            rendered = temp_dir / f"slide-{index:02d}.png"
            if slide.image_name is None:
                _closing_slide(slide, rendered)
            else:
                _captioned_slide(media_dir / slide.image_name, slide, rendered)
            slide_paths.append(rendered)
        _encode(_ffmpeg_executable(args.ffmpeg), slide_paths, output)

    print(output)


if __name__ == "__main__":
    main()
