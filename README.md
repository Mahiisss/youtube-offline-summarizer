Offline YouTube Video Summarizer

Whisper Small (Offline STT) + BART Large CNN (Offline Summarization)

1. Overview

This project implements a fully offline system that downloads audio from a YouTube URL, transcribes it using Whisper Small (CTranslate2), cleans the transcript, and generates an abstractive summary using a local BART Large CNN model.
All processing is performed locally without any cloud APIs, making the system suitable for restricted or offline environments.

Pipeline:
YouTube URL → Audio Download → Whisper Transcription → Transcript Cleaning → BART Summarization → Final Summary

2. Features

Offline Whisper Small speech-to-text

Offline summarization using BART Large CNN snapshot

Modular architecture for easier debugging and extension

Transcript cleaning and normalization

Chunk-based summarization to handle long transcripts

lyric/music detection

CLI commands and PowerShell automation script

3. Repository Structure
youtube-offline-summarizer/
│
├── run_full_pipeline.ps1
│
├── src/
│   ├── download_audio.py
│   ├── stt_whisper.py
│   ├── summarize_text_improved.py
│
├── scripts/
│   └── normalize_text.py
│
├── models/
│   └── bart/     
│
├── demo/
│   ├── *.wav
│   ├── *.whisper.txt
│   ├── *.whisper.clean.txt
│   └── *.summary.txt
│
└── requirements.txt

4. Environment Setup
Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

Install FFmpeg

Download FFmpeg, extract it, and note the bin folder path:

C:\tools\ffmpeg\ffmpeg-8.0.1-essentials_build\bin

Download offline BART model

Place the BART snapshot here:

models/bart/models--facebook--bart-large-cnn/snapshots/<snapshot-id>/

5. Model Choices and Rationale
Whisper Small (CTranslate2)

Chosen for its balance of speed, accuracy, and CPU efficiency.
Larger Whisper models provide minor accuracy gains but are too slow for offline CPU-only execution. Whisper Small with CTranslate2 delivers fast, reproducible transcription.

BART Large CNN

Selected for its strong performance on abstractive summarization.
It handles lecture-style content well, produces coherent summaries, and runs reliably from a local snapshot.

Chunked Summarization

Since BART accepts only ~1024 tokens per pass, long transcripts must be split into smaller sections.
Each chunk is summarized independently and merged for a final summary.

Transcript Cleaning

A dedicated normalization script removes filler words, duplicated fragments, spacing issues, and ASR noise.
Cleaner input meaningfully improves summarization quality.

Lyric/Music Detection

Avoids generating meaningless summaries for songs, which often contain repetition and little semantic content.
A --force flag bypasses detection when required.

Modular Design

Downloading, transcription, cleaning, and summarization are separated into individual modules.
This structure mirrors production ML systems and keeps debugging simple.

6. Running the Pipeline

Using demo video:
https://youtu.be/rNxC16mlO60

Step 1: Download audio
python src/download_audio.py --url "https://youtu.be/rNxC16mlO60" --out demo --ffmpeg-location "C:\tools\ffmpeg\ffmpeg-8.0.1-essentials_build\bin"

Step 2: Transcribe
python src/stt_whisper.py --wav ".\demo\rNxC16mlO60.wav" --out ".\demo\rNxC16mlO60.whisper.txt" --model small --device cpu

Step 3: Clean transcript
python scripts/normalize_text.py ".\demo\rNxC16mlO60.whisper.txt" ".\demo\rNxC16mlO60.whisper.clean.txt"

Step 4: Summarize
python src/summarize_text_improved.py ^
  --transcript ".\demo\rNxC16mlO60.whisper.clean.txt" ^
  --model_name_or_path "<ABSOLUTE_PATH_TO_BART_SNAPSHOT>" ^
  --out ".\demo\rNxC16mlO60.improved.summary.txt" ^
  --num_beams 6 --max_length 150 --min_length 50 --length_penalty 0.9 --device cpu --force

7. Final Summary

This is the final summary produced for the demo video, included exactly as generated:

George Hood set the world record for the longest plank in history. He kept going for an hour, for two hours, and then 10 hours. Hood said he kept his mind busy, distracting himself by focusing on the conversations in the room.

Grit isn't just about willpower. It's rooted in biology. The most powerful indicator to date is a protein that we're just starting to understand called brain derived neurotrophic factor, or BDNF. BDNF is crucial for things like memory and mental resilience.

No one has ever studied BDNF during a plank. What we know is this. The most effective exercises for raising BDNF levels are those requiring mental effort. In people, activities such as yoga, of all things, that combine physical effort and concentration have produced some of the highest levels of BDNF ever measured.

The next time you feel you need more grit in your life, do a plank. If you can't get on the floor, do it against the wall. It only takes a minute, but that minute can be transformative. George, Daniel, and my patients deserve as much.

8. Challenges and Solutions
Challenge	Reason	Solution
Repetition in Whisper output	ASR artifact in long speech	Added transcript normalization
BART token limit	Only ~1024 tokens supported	Introduced chunk-based summarization
Poor summaries for songs	Repetition and low meaning	Implemented lyric/music detection
Offline summarization required	HuggingFace usually downloads at runtime	Included full local model snapshot
Multi-step execution	Hard to reproduce	Added PowerShell wrapper script
9. Checklist

Activate environment

Download audio

Transcribe with Whisper

Normalize the transcript

Run summarizer

Open final summary file

10. Final Notes

This system is designed to function entirely offline with a clean, production-style architecture. Whisper Small provides efficient CPU-based transcription, while BART Large CNN produces high-quality abstractive summaries. The pipeline includes input cleaning, chunked summarization, and optional lyric detection to ensure robust performance across diverse YouTube videos.