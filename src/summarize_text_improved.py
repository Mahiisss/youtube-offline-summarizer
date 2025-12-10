#!/usr/bin/env python3
"""
summarize_text_improved.py
Chunked summarization with music/lyrics detection and safe output directory creation.
Usage example (PowerShell):
 python src/summarize_text_improved.py `
   --transcript .\demo\input.whisper.clean.txt `
   --model_name_or_path "C:/.../snapshot" `
   --out .\demo\input.summary.txt `
   --num_beams 6 --max_length 150 --min_length 50 --length_penalty 0.9 --device cpu --chunk_words 400 --force
"""
import argparse
import os
import sys
from transformers import BartTokenizer, BartForConditionalGeneration

# -------------------------
def looks_like_lyrics(text: str):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) < 8:
        return False
    short_lines = sum(1 for l in lines if len(l) <= 45)
    short_ratio = short_lines / len(lines)
    repeated_phrases = 0
    seen = {}
    for l in lines:
        seen[l] = seen.get(l, 0) + 1
    for v in seen.values():
        if v >= 3:
            repeated_phrases += 1
    return short_ratio > 0.70 and repeated_phrases >= 2

def chunk_text(text, max_words=250):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)
    return chunks

def summarize_chunk(chunk, model, tokenizer, args):
    inputs = tokenizer(
        chunk,
        return_tensors="pt",
        max_length=1024,
        truncation=True
    )
    summary_ids = model.generate(
        inputs["input_ids"],
        num_beams=args.num_beams,
        max_length=args.max_length,
        min_length=args.min_length,
        length_penalty=args.length_penalty,
        no_repeat_ngram_size=3
    )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

def main():
    parser = argparse.ArgumentParser(description="Improved text summarizer")
    parser.add_argument("--transcript", required=True, help="Path to cleaned transcript")
    parser.add_argument("--model_name_or_path", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--num_beams", type=int, default=4)
    parser.add_argument("--max_length", type=int, default=120)
    parser.add_argument("--min_length", type=int, default=30)
    parser.add_argument("--length_penalty", type=float, default=0.9)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--force", action="store_true", help="Ignore music/lyrics detection and force summarization")
    parser.add_argument("--chunk_words", type=int, default=250, help="Words per chunk for long transcripts")
    args = parser.parse_args()

    if not os.path.exists(args.transcript):
        print(f"ERROR: transcript not found: {args.transcript}")
        sys.exit(1)

    with open(args.transcript, "r", encoding="utf8") as f:
        text = f.read().strip()

    is_music = looks_like_lyrics(text)
    if is_music and not args.force:
        print(f"Skipped summarization: detected music/lyrics. Wrote note to {args.out}")
        os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf8") as f:
            f.write("Detected likely music/lyrics — summarization skipped.\n")
        sys.exit(0)

    if is_music and args.force:
        print("⚠️  Warning: Lyrics/music detected, but --force was used. Summarizing anyway.")

    # Load model tokenizer
    print(f"Loading BART model from: {args.model_name_or_path}")
    tokenizer = BartTokenizer.from_pretrained(args.model_name_or_path, local_files_only=True)
    model = BartForConditionalGeneration.from_pretrained(args.model_name_or_path, local_files_only=True)
    # optional: move model to device if desired (torch device), but local_files_only is key for offline

    # chunk + summarize
    chunks = chunk_text(text, max_words=args.chunk_words)
    final_sum = []
    print(f"Found {len(chunks)} chunks")
    for i, ch in enumerate(chunks, 1):
        print(f"Summarizing chunk {i}/{len(chunks)}...")
        out = summarize_chunk(ch, model, tokenizer, args)
        final_sum.append(out)

    summary = "\n".join(final_sum).strip()

    # ensure output dir exists
    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(args.out, "w", encoding="utf8") as f:
        f.write(summary)

    print(f"\nSaved summary to {args.out}")

if __name__ == "__main__":
    main()
