"""Copy original recordings and derive web posters from their actual frames."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

import cv2
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageOps


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frame_at(path, seconds):
    capture = cv2.VideoCapture(str(path))
    capture.set(cv2.CAP_PROP_POS_MSEC, seconds * 1000)
    success, frame = capture.read()
    metadata = {"width": int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "fps": capture.get(cv2.CAP_PROP_FPS),
                "frames": int(capture.get(cv2.CAP_PROP_FRAME_COUNT))}
    capture.release()
    if not success:
        raise RuntimeError(f"Could not decode {path}")
    return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)), metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    args = parser.parse_args()
    site = Path(__file__).resolve().parents[1]
    media = site / "assets/media"
    images = site / "assets/images"
    media.mkdir(parents=True, exist_ok=True)
    images.mkdir(parents=True, exist_ok=True)
    clips = ["closed_loop_465d43bf893d5e66.mp4", "closed_loop_81c70798936b5140.mp4",
             "closed_loop_af6ce3c064fa5a56.mp4", "closed_loop_b5668089b793502b.mp4"]
    showcase = media / "closed_loop_showcase.mp4"
    with tempfile.TemporaryDirectory() as temporary:
        concat = Path(temporary) / "clips.txt"
        concat.write_text("".join("file '" + str((args.source / name).resolve()).replace("'", "'\\''") + "'\n" for name in clips))
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
                        "-f", "concat", "-safe", "0", "-i", str(concat),
                        "-map", "0:v:0", "-c", "copy", "-movflags", "+faststart",
                        str(showcase)], check=True)
    videos = {"real_raster_multiview.mp4": "matched-poster",
              "closed_loop_showcase.mp4": "showcase-poster"}
    manifest = []
    for name, poster in videos.items():
        source = showcase if name == showcase.name else args.source / name
        destination = media / name
        if source != destination:
            shutil.copy2(source, destination)
        assert digest(source) == digest(destination)
        frame, metadata = frame_at(destination, 1.0)
        frame.save(images / f"{poster}.webp", quality=95)
        item = {"source": name, "sha256": digest(destination),
                "encoding": "stream-copy concat" if name == showcase.name else "original file",
                "poster_time_s": 1.0, **metadata}
        if name == showcase.name:
            assert metadata["frames"] == 528 and metadata["fps"] == 24
            item["inputs"] = [{"file": clip, "sha256": digest(args.source / clip)} for clip in clips]
        manifest.append(item)

    # Keep the complete multiview frame; do not invent or rearrange observations.
    frame, _ = frame_at(media / "real_raster_multiview.mp4", 1.0)
    thumbnail = Image.new("RGB", (1120, 640), "#f5f7f7")
    scaled = ImageOps.contain(frame, (1120, 560), Image.Resampling.LANCZOS)
    thumbnail.paste(scaled, ((1120 - scaled.width) // 2, (640 - scaled.height) // 2))
    thumbnail.save(images / "grad-thumbnail.webp", quality=95)

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    social = Image.new("RGB", (1200, 630), "white")
    draw = ImageDraw.Draw(social)
    draw.text((55, 28), "GRAD", font=ImageFont.truetype(bold_path, 66), fill="#20272b")
    draw.text((58, 112), "Geometric Rasterization for Visual Driving",
              font=ImageFont.truetype(font_path, 27), fill="#50616a")
    scaled = ImageOps.contain(frame, (1090, 400), Image.Resampling.LANCZOS)
    social.paste(scaled, ((1200 - scaled.width) // 2, 188))
    social.save(images / "grad-social.jpg", quality=96)
    icon = Image.new("RGB", (128, 128), "#176c8f")
    draw = ImageDraw.Draw(icon)
    draw.text((64, 64), "SJ", anchor="mm", font=ImageFont.truetype(bold_path, 62), fill="white")
    icon.save(images / "favicon.png")
    (site / "scripts/media-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
