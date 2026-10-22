import os
#!/usr/bin/env python3
"""StoryCast fade — end fade-to-black + audio fade for a finished cut.

Usage:
  python3 fade.py final.mp4 [--seconds 1.3]
Writes final-faded.mp4 (or overwrites with --replace).
"""
import argparse
import subprocess
import sys


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        sys.exit(f"cannot read duration of {path} — is it a media file?")


def has_video(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=index", "-of", "csv=p=0", path], capture_output=True, text=True)
    return bool(out.stdout.strip())


def main():
    ap = argparse.ArgumentParser(description="StoryCast end fade")
    ap.add_argument("video")
    ap.add_argument("--seconds", type=float, default=1.3)
    ap.add_argument("--replace", action="store_true", help="overwrite the input file")
    args = ap.parse_args()

    d = duration(args.video)
    st = max(0.0, d - args.seconds)
    root, ext = args.video.rsplit(".", 1)
    out = root + "-fade-tmp." + ext if args.replace else f"{root}-faded.{ext}"
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", args.video,
           "-af", f"afade=t=out:st={st:.2f}:d={args.seconds}"]
    if has_video(args.video):
        cmd += ["-vf", f"fade=t=out:st={st:.2f}:d={args.seconds}",
                "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                "-pix_fmt", "yuv420p"]
    cmd += ["-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    if args.replace:
        os.replace(out, args.video)
        out = args.video
    print(f"OK {out}: fade from {st:.1f}s to {d:.1f}s")


if __name__ == "__main__":
    main()
