from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the HTML intro animation to MP4 and GIF.")
    parser.add_argument("--html", default="docs/project-intro-animation.html")
    parser.add_argument("--mp4", default="outputs/project-intro-animation.mp4")
    parser.add_argument("--gif", default="docs/assets/intro-animation-preview.gif")
    parser.add_argument("--fps", type=int, default=8)
    parser.add_argument("--duration", type=float, default=48.0)
    parser.add_argument("--start-offset", type=float, default=0.6)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--device-scale-factor", type=float, default=1.0)
    parser.add_argument("--mp4-crf", type=int, default=21)
    parser.add_argument("--skip-gif", action="store_true")
    args = parser.parse_args()

    html_path = Path(args.html).resolve()
    mp4_path = Path(args.mp4).resolve()
    gif_path = Path(args.gif).resolve()
    if not html_path.exists():
        raise SystemExit(f"missing animation html: {html_path}")

    ffmpeg = find_executable("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg was not found on PATH")

    with tempfile.TemporaryDirectory() as tmp:
        frames_dir = Path(tmp) / "frames"
        frames_dir.mkdir()
        capture_frames(
            html_path=html_path,
            frames_dir=frames_dir,
            fps=args.fps,
            duration=args.duration,
            start_offset=args.start_offset,
            width=args.width,
            height=args.height,
            device_scale_factor=args.device_scale_factor,
        )
        mp4_path.parent.mkdir(parents=True, exist_ok=True)
        gif_path.parent.mkdir(parents=True, exist_ok=True)
        render_mp4(ffmpeg, frames_dir, args.fps, mp4_path, args.mp4_crf)
        if not args.skip_gif:
            render_gif(ffmpeg, frames_dir, args.fps, gif_path)

    print(mp4_path)
    if not args.skip_gif:
        print(gif_path)
    return 0


def capture_frames(
    html_path: Path,
    frames_dir: Path,
    fps: int,
    duration: float,
    start_offset: float,
    width: int,
    height: int,
    device_scale_factor: float,
) -> None:
    browser_path = find_browser()
    if not browser_path:
        raise SystemExit("Chrome or Edge was not found for frame capture")
    frame_count = max(1, int((duration - start_offset) * fps))
    profile_dir = frames_dir.parent / "chrome-profile"
    for index in range(frame_count):
        t = min(start_offset + index / fps, duration - 0.001)
        out = frames_dir / f"frame_{index:04d}.png"
        url = f"{html_path.as_uri()}?capture=1&t={t:.4f}"
        command = [
            browser_path,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--hide-scrollbars",
            f"--user-data-dir={profile_dir}",
            f"--window-size={width},{height}",
            f"--force-device-scale-factor={device_scale_factor}",
            "--virtual-time-budget=800",
            f"--screenshot={out.resolve()}",
            url,
        ]
        subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)


def render_mp4(ffmpeg: str, frames_dir: Path, fps: int, output: Path, crf: int) -> None:
    command = [
        ffmpeg,
        "-y",
        "-framerate",
        str(fps),
        "-i",
        str(frames_dir / "frame_%04d.png"),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        str(crf),
        "-movflags",
        "+faststart",
        str(output),
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)


def render_gif(ffmpeg: str, frames_dir: Path, fps: int, output: Path) -> None:
    palette = output.with_suffix(".palette.png")
    preview_filter = "fps=5,scale=960:-1:flags=lanczos"
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-framerate",
            str(fps),
            "-i",
            str(frames_dir / "frame_%04d.png"),
            "-vf",
            f"{preview_filter},palettegen=max_colors=96",
            str(palette),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    try:
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-framerate",
                str(fps),
                "-i",
                str(frames_dir / "frame_%04d.png"),
                "-i",
                str(palette),
                "-lavfi",
                f"{preview_filter}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5",
                str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        palette.unlink(missing_ok=True)


def find_executable(name: str) -> str | None:
    return shutil.which(name) or shutil.which(f"{name}.exe")


def find_browser() -> str | None:
    candidates = [
        shutil.which("chrome"),
        shutil.which("chrome.exe"),
        shutil.which("msedge"),
        shutil.which("msedge.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    return None


if __name__ == "__main__":
    raise SystemExit(main())
