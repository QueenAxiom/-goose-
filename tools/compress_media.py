"""Compress photos and videos in place (standing rule: compress before posting).

Usage: python tools/compress_media.py <file-or-folder> [...]

Keeps filenames and formats so links don't break. A file is only replaced when the
compressed copy is smaller, so re-running is safe. Originals live in git history.
Needs ffmpeg on PATH.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

JPEG_QUALITY = "6"  # ffmpeg -q:v, 2 (best) to 31 (worst)
VIDEO_CRF = "28"  # H.264, 23 is default, higher is smaller
VIDEO_MAX_HEIGHT = 1080
AUDIO_BITRATE = "96k"
TIMEOUT_SECONDS = 1800
MIN_SAVING_RATIO = 0.98  # skip replacing for gains under 2%

PNG_FILTER = "split[a][b];[a]palettegen=max_colors=256[p];[b][p]paletteuse=dither=sierra2_4a"
VIDEO_FILTER = f"scale=-2:'min({VIDEO_MAX_HEIGHT},ih)'"


def build_command(src: Path, dst: Path) -> "list[str] | None":
    """ffmpeg command for this file type, or None if the type is not handled."""
    ext = src.suffix.lower()
    base = ["ffmpeg", "-v", "error", "-y", "-i", str(src)]
    if ext in (".jpg", ".jpeg"):
        return base + ["-q:v", JPEG_QUALITY, str(dst)]
    if ext == ".png":
        return base + ["-vf", PNG_FILTER, "-c:v", "png", "-f", "image2", str(dst)]
    if ext == ".webp":
        return base + ["-q:v", "70", str(dst)]
    if ext in (".mp4", ".mov", ".m4v"):
        return base + ["-vf", VIDEO_FILTER, "-c:v", "libx264", "-crf", VIDEO_CRF,
                       "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                       "-c:a", "aac", "-b:a", AUDIO_BITRATE, str(dst)]
    return None


def compress_file(src: Path) -> "tuple[int, int] | None":
    """Compress one file in place. Returns (before, after) bytes if replaced, else None."""
    with tempfile.TemporaryDirectory() as tmp:
        dst = Path(tmp) / src.name
        cmd = build_command(src, dst)
        if cmd is None:
            return None
        subprocess.run(cmd, check=True, timeout=TIMEOUT_SECONDS)
        before, after = src.stat().st_size, dst.stat().st_size
        if after >= before * MIN_SAVING_RATIO:
            return None
        shutil.move(str(dst), str(src))
        return before, after


def iter_files(paths: "list[str]"):
    for raw in paths:
        p = Path(raw)
        yield from (sorted(f for f in p.rglob("*") if f.is_file()) if p.is_dir() else [p])


def main(argv: "list[str]") -> int:
    if not argv or shutil.which("ffmpeg") is None:
        print(__doc__)
        return 1
    saved_total = 0
    for f in iter_files(argv):
        try:
            result = compress_file(f)
        except (subprocess.SubprocessError, OSError) as exc:
            print(f"FAILED  {f}: {exc}")
            continue
        if result:
            saved_total += result[0] - result[1]
            print(f"{result[0] // 1024:>6} KB -> {result[1] // 1024:>6} KB  {f}")
    print(f"saved {saved_total // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
