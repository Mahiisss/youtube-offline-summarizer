
#  patch for src/summarizer.py 

import argparse
from pathlib import Path
import torch
import os

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
# put near top of file next to other imports
import re, statistics
from pathlib import Path

def looks_like_music(transcript_text: str):
    # quick heuristic: many short lines + repeated lines + low avg words/line
    lines = [l.strip() for l in transcript_text.splitlines() if l.strip()]
    if not lines:
        return False
    avg_words = statistics.mean([len(l.split()) for l in lines])
    # repetition ratio of exact consecutive line repeats
    repeats = sum(1 for i in range(len(lines)-1) if lines[i]==lines[i+1])
    repetition_ratio = repeats / max(1, len(lines))
    short_line_ratio = sum(1 for l in lines if len(l.split()) <= 5) / len(lines)
    # Heuristics: many short lines or repeated lines -> likely lyrics
    return (avg_words < 6 and short_line_ratio > 0.5) or repetition_ratio > 0.03


def main():
    parser = argparse.ArgumentParser(description="Summarize transcript (offline)")
    parser.add_argument("--transcript", required=True, help="Path to transcript txt")
    parser.add_argument("--model_name_or_path", required=True, help="Local model folder or HF id")
    parser.add_argument("--out", required=True, help="Output file for final summary")
    # tuning params exposed
    parser.add_argument("--max_length", type=int, default=200, help="max tokens in final summary")
    parser.add_argument("--min_length", type=int, default=40, help="min tokens in final summary")
    parser.add_argument("--num_beams", type=int, default=4, help="beam size for generation")
    parser.add_argument("--length_penalty", type=float, default=1.0, help="length penalty for generation")
    parser.add_argument("--device", default="cpu", help="device: cpu or cuda")
    args = parser.parse_args()

    device = torch.device(args.device if torch.cuda.is_available() or args.device == "cpu" else "cpu")
    print("DEBUG: model_name_or_path arg:", args.model_name_or_path)
    print("DEBUG: exists on disk?:", os.path.exists(args.model_name_or_path))
    print("DEBUG: abs path:", os.path.abspath(args.model_name_or_path))
   
   


    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path, local_files_only=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_name_or_path, local_files_only=True).to(device)

    txt = Path(args.transcript).read_text(encoding="utf8")
    if looks_like_music(txt):
        # write a small note instead of running summarizer
        msg = "Detected likely music/lyrics content — summarization skipped."
        Path(args.out).write_text(msg, encoding="utf8")
        print("Skipped summarization: detected music/lyrics. Wrote note to", args.out)
        return
    # Simple chunking by words to fit model (you already had chunking; this is a safe default)
    words = txt.split()
    chunk_size_words = 600  # tweak if needed
    chunks = [" ".join(words[i:i+chunk_size_words]) for i in range(0, len(words), chunk_size_words)]

    chunk_summaries = []
    for i, chunk in enumerate(chunks, start=1):
        print(f"Summarizing chunk {i}/{len(chunks)} (approx {len(chunk.split())} words)...")
        # add a short prefix for models like t5
        prefix = ""
        if hasattr(tokenizer, "name_or_path") and tokenizer.name_or_path and "t5" in tokenizer.name_or_path:
            prefix = "summarize: "
        meta_in = prefix + chunk
        input_ids = tokenizer.encode(meta_in, return_tensors="pt", truncation=True).to(device)
        out_ids = model.generate(
            input_ids,
            max_length=args.max_length,
            min_length=args.min_length,
            num_beams=args.num_beams,
            early_stopping=True,
            length_penalty=args.length_penalty,
            no_repeat_ngram_size=3,
        )
        chunk_summary = tokenizer.decode(out_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
        chunk_summaries.append(chunk_summary)

    # final summarization (summarize concatenated chunk summaries if more than 1)
    meta_in = " ".join(chunk_summaries)
    if hasattr(tokenizer, "name_or_path") and tokenizer.name_or_path and "t5" in tokenizer.name_or_path:
        meta_in = "summarize: " + meta_in
    input_ids = tokenizer.encode(meta_in, return_tensors="pt", truncation=True).to(device)
    out_ids = model.generate(
        input_ids,
        max_length=args.max_length,
        min_length=args.min_length,
        num_beams=args.num_beams,
        early_stopping=True,
        length_penalty=args.length_penalty,
        no_repeat_ngram_size=3,
    )
    final_summary = tokenizer.decode(out_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
    Path(args.out).write_text(final_summary, encoding="utf8")
    print("Saved:", args.out)

if __name__ == "__main__":
    main()
# --- end patch ---
