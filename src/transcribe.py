import argparse
import os
import sys
import wave
import soundfile as sf
from pathlib import Path

try:
    import vosk
except Exception as e:
    print("Vosk import error:", e)
    print("Install with: pip install vosk")
    raise

def ensure_wav_path(wav_path: str):
    p = Path(wav_path)
    if not p.exists():
        raise FileNotFoundError(f"WAV file not found: {wav_path}")
    return str(p)

def transcribe_vosk(wav: str, model_dir: str, out_txt: str):
    wav = ensure_wav_path(wav)
    model_dir = Path(model_dir)
    if not model_dir.exists() or not model_dir.is_dir():
        raise FileNotFoundError(f"Vosk model folder not found: {model_dir}")

    # normalize sample rate to 16000 and write temp
    data, sr = sf.read(wav)
    if sr != 16000:
        import soundfile as sf
        import numpy as np
        tmp = Path(wav).with_name(Path(wav).stem + "_16k.wav")
        sf.write(tmp, data, 16000)
        use_wav = str(tmp)
    else:
        use_wav = wav

    print("Transcribing with Vosk...")
    model = vosk.Model(str(model_dir))
    wf = wave.open(use_wav, "rb")
    rec = vosk.KaldiRecognizer(model, wf.getframerate())
    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            results.append(rec.Result())
    results.append(rec.FinalResult())

    # write a simple text file with concatenated text
    import json, re
    text = " ".join(json.loads(r).get("text", "") for r in results)
    # very small cleanup
    text = re.sub(r"\s+", " ", text).strip()
    Path(out_txt).write_text(text, encoding="utf8")
    print("Saved transcript:", out_txt)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wav", required=True)
    parser.add_argument("--model", required=True, help="Vosk model folder (e.g. models/vosk-model-small-en-us-0.15)")
    parser.add_argument("--out", default=None, help="Output text file. If omitted will create <wavname>_16k.vosk.txt")
    args = parser.parse_args()

    out = args.out or str(Path(args.wav).with_suffix("").name + "_16k.vosk.txt")
    try:
        transcribe_vosk(args.wav, args.model, out)
    except Exception as e:
        print("ERROR:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
