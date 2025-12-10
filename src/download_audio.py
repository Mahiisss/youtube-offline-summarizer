""" YouTube audio downloader using yt-dlp.
Saves a .wav file into the specified output directory """
import argparse
import os
import sys
from yt_dlp import YoutubeDL

def download_audio(youtube_url: str, out_dir: str = "demo", ffmpeg_location: str | None = None):
    os.makedirs(out_dir, exist_ok=True)
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(out_dir, "%(id)s.%(ext)s"),
        "quiet": False,
        "no_warnings": True,
        "ignoreerrors": False,
        "noplaylist": True,
        # convert to wav with ffmpeg
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
            "preferredquality": "192",
        }],
        "postprocessor_args": [
            "-ar", "16000"
        ],
        "prefer_ffmpeg": True,
    }

    if ffmpeg_location:
        # yt-dlp accepts "--ffmpeg-location" via options dict as 'ffmpeg_location'
        ydl_opts["ffmpeg_location"] = ffmpeg_location

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        if info is None:
            raise RuntimeError("yt-dlp returned no info (video may be private/removed).")
        vid_id = info.get("id") or info.get("url") or "output"
        out_path = os.path.join(out_dir, f"{vid_id}.wav")
        if not os.path.exists(out_path):
            # sometimes yt-dlp appends extension differently; try to find the created file
            for f in os.listdir(out_dir):
                if f.startswith(vid_id) and f.endswith(".wav"):
                    out_path = os.path.join(out_dir, f)
                    break
        return out_path

def main():
    parser = argparse.ArgumentParser(description="Download audio from YouTube (wav)")
    parser.add_argument("--url", "-u", required=True, help="YouTube video URL")
    parser.add_argument("--out", "-o", default="demo", help="Output directory")
    parser.add_argument("--ffmpeg-location", default=None, help="Path to ffmpeg bin (optional)")
    args = parser.parse_args()
    try:
        out = download_audio(args.url, args.out, args.ffmpeg_location)
        print("Saved audio to:", out)
    except Exception as e:
        print("ERROR:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
