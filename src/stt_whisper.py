"""
Offline transcription using faster-whisper (ctranslate2 backend).
Usage examples:
  # CPU, small model:
  python src/transcribe_whisper.py --wav .\demo\2Vv-BfVoq4g.wav --out .\demo\2Vv-BfVoq4g.whisper.txt --model small --device cpu

  # If you have GPU and enough memory:
  python src/transcribe_whisper.py --wav .\demo\2Vv-BfVoq4g.wav --out .\demo\2Vv-BfVoq4g.whisper.txt --model small --device cuda --compute_type float16
"""
import argparse
import json
import sys
from pathlib import Path

try:
    from faster_whisper import WhisperModel
except Exception as e:
    print("ERROR: faster_whisper import failed:", e)
    print("Install with: pip install faster-whisper ctranslate2")
    sys.exit(1)


def transcribe(wav_path: str, out_path: str, model_size="small", device="cpu", compute_type=None, language=None):
    # ensure compute_type is a string acceptable to ctranslate2 (not None)
    ct_compute_type = compute_type if compute_type is not None else "default"

    # Validate wav path
    wav = Path(wav_path)
    if not wav.exists():
        raise FileNotFoundError(f"WAV file not found: {wav}")

    print(f"Loading model: {model_size}  device: {device}  compute_type: {ct_compute_type}")
    try:
        model = WhisperModel(model_size, device=device, compute_type=ct_compute_type)
    except TypeError as e:
        # Common: constructor signature mismatch or None passed where string expected
        raise RuntimeError(
            f"Model construction failed (TypeError). check faster-whisper / ctranslate2 versions and compute_type. "
            f"Original error: {e}"
        ) from e
    except RuntimeError as e:
        # CUDA out of memory
        raise

    # transcribe: returning (segments, info)
    # beam_size and other options can be tuned
    segments, info = model.transcribe(str(wav), beam_size=5, language=language, vad_filter=False, word_timestamps=False)

    out_txt = Path(out_path)
    out_json = out_txt.with_suffix(out_txt.suffix + ".segments.json")

    # collect lines and segments
    lines = []
    segs = []
    for seg in segments:
        # faster-whisper segments may be objects with attributes 
        if isinstance(seg, dict):
            start = seg.get("start", 0.0)
            end = seg.get("end", 0.0)
            text = seg.get("text", "")
        else:
            # object-like has .start, .end, .text
            start = getattr(seg, "start", getattr(seg, "start_time", 0.0))
            end = getattr(seg, "end", getattr(seg, "end_time", 0.0))
            text = getattr(seg, "text", str(seg))

        segs.append({"start": float(start), "end": float(end), "text": text})
        lines.append(f"{float(start):.2f} --> {float(end):.2f}\n{text.strip()}\n")

    out_txt.write_text("\n".join(lines), encoding="utf8")
    out_json.write_text(json.dumps(segs, ensure_ascii=False, indent=2), encoding="utf8")

    print("Saved transcript:", out_txt)
    print("Saved segments json:", out_json)
    return out_txt, out_json


def main():
    parser = argparse.ArgumentParser(description="Transcribe wav with faster-whisper (offline)")
    parser.add_argument("--wav", required=True, help="Path to WAV file")
    parser.add_argument("--out", required=True, help="Output transcript path (e.g. demo/out.whisper.txt)")
    parser.add_argument("--model", default="small", help="Model size or path (small, medium, etc. or local folder)")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"], help="Device to run on")
    parser.add_argument("--compute_type", default=None,
                        help="Compute type for ctranslate2: e.g. 'default', 'float16', 'int8'. If not set, defaults to 'default'.")
    parser.add_argument("--language", default=None, help="Language code (e.g. 'en') or leave empty for autodetect")
    args = parser.parse_args()

    try:
        transcribe(
            wav_path=args.wav,
            out_path=args.out,
            model_size=args.model,
            device=args.device,
            compute_type=args.compute_type,
            language=args.language
        )
    except FileNotFoundError as e:
        print("ERROR:", e)
        sys.exit(2)
    except RuntimeError as e:
        #  CUDA OOM , runtime issue
        print("RUNTIME ERROR:", e)
        print("If this is CUDA OOM, try --device cpu or use a smaller model (tiny/base).")
        sys.exit(3)
    except Exception as e:
        print("Unexpected error:", e)
        sys.exit(4)


if __name__ == "__main__":
    main()
