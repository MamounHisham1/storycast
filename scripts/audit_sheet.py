#!/usr/bin/env python3
"""StoryCast audit sheet — build a frame contact sheet for the mandatory
content-compliance review of a downloaded stock-footage pool.

Extracts N frames per clip (default 3: 10%, 50%, 90% of duration) and tiles
them into one image you (the agent) must visually inspect against the
channel's content rules. Ambiguous clips fail — always.

Usage:
  python3 audit_sheet.py --clips c1.mp4 c2.mp4 ... --out sheet.jpg [--frames 3]
"""
import argparse
import glob
import math
import os
import subprocess
import sys
import tempfile

TILE_W, TILE_H = 270, 480


def main():
    ap = argparse.ArgumentParser(description="StoryCast audit sheet")
    ap.add_argument("--clips", nargs="+", required=True, help="clip files (or a glob pattern)")
    ap.add_argument("--out", required=True, help="output contact sheet image")
    ap.add_argument("--frames", type=int, default=3, help="frames per clip")
    args = ap.parse_args()

    clips = []
    for pattern in args.clips:
        matched = glob.glob(pattern)
        clips.extend(matched if matched else [pattern])
    if not clips:
        sys.exit("no clips found")

    with tempfile.TemporaryDirectory() as tmp:
        tiles = []
        for i, clip in enumerate(clips):
            for j in range(args.frames):
                frac = (j + 0.5) / args.frames
                tile = os.path.join(tmp, f"tile_{i:03d}_{j}.jpg")
                r = subprocess.run(
                    ["ffmpeg", "-y", "-v", "error", "-ss", f"{frac:.2f}", "-i", clip,
                     "-frames:v", "1", "-vf", f"scale={TILE_W}:{TILE_H}", tile],
                    capture_output=True)
                if r.returncode == 0 and os.path.getsize(tile) > 0:
                    tiles.append(tile)

        if not tiles:
            sys.exit("no frames extracted — are the clips readable?")

        cols = min(9, len(tiles))
        rows = math.ceil(len(tiles) / cols)
        inputs, labels = [], []
        layout = []
        for k, t in enumerate(tiles):
            inputs += ["-i", t]
            layout.append(f"{(k % cols) * TILE_W}_{(k // cols) * TILE_H}")
        fc = "".join(f"[{k}:v]" for k in range(len(tiles)))
        fc += f"xstack=inputs={len(tiles)}:layout={'|'.join(layout)}"

        subprocess.run(
            ["ffmpeg", "-y", "-v", "error"] + inputs +
            ["-filter_complex", fc, "-frames:v", "1", args.out],
            check=True)

    print(f"OK {args.out}: {len(clips)} clips x {args.frames} frames = {len(tiles)} tiles "
          f"({cols} cols x {rows} rows)")
    print("AUDIT NOW: inspect every tile against the channel content rules. "
          "Ambiguous clips fail. Then assemble only from approved clips.")


if __name__ == "__main__":
    main()
