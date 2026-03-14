🎬 Offline YouTube Video Summarizer

Whisper Small (Offline STT) + BART Large CNN (Offline Summarization)

A fully offline NLP pipeline that downloads audio from a YouTube video, transcribes it using Whisper Small, cleans the transcript, and generates an abstractive summary using BART Large CNN.

The entire system runs locally without any cloud APIs, making it suitable for offline or restricted environments.

🚀 Pipeline
YouTube URL
   ↓
Audio Download
   ↓
Whisper Transcription
   ↓
Transcript Cleaning
   ↓
BART Summarization
   ↓
Final Summary
✨ Features

🎤 Offline speech-to-text using Whisper Small (CTranslate2)

🧠 Abstractive summarization using BART Large CNN

🧹 Transcript cleaning and normalization

🧩 Chunk-based summarization for long transcripts

🎵 Lyric / music detection to avoid meaningless summaries

🧱 Modular pipeline architecture

💻 CLI commands for running each stage

⚙️ PowerShell automation script

📂 Repository Structure
youtube-offline-summarizer/
│
├── run_full_pipeline.ps1
│
├── src/
│   ├── download_audio.py
│   ├── stt_whisper.py
│   └── summarize_text_improved.py
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
⚙️ Environment Setup
1️⃣ Create Virtual Environment
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
2️⃣ Install FFmpeg

Download FFmpeg and add the bin directory:

C:\tools\ffmpeg\ffmpeg-8.0.1-essentials_build\bin
3️⃣ Download Offline BART Model

Place the model snapshot in:

models/bart/models--facebook--bart-large-cnn/snapshots/<snapshot-id>/
▶ Running the Pipeline

Example demo video:

https://youtu.be/rNxC16mlO60

Step 1 — Download Audio
python src/download_audio.py \
--url "https://youtu.be/rNxC16mlO60" \
--out demo \
--ffmpeg-location "C:\tools\ffmpeg\ffmpeg-8.0.1-essentials_build\bin"
Step 2 — Transcribe with Whisper
python src/stt_whisper.py \
--wav ".\demo\rNxC16mlO60.wav" \
--out ".\demo\rNxC16mlO60.whisper.txt" \
--model small \
--device cpu
Step 3 — Clean Transcript
python scripts/normalize_text.py \
".\demo\rNxC16mlO60.whisper.txt" \
".\demo\rNxC16mlO60.whisper.clean.txt"
Step 4 — Generate Summary
python src/summarize_text_improved.py \
--transcript ".\demo\rNxC16mlO60.whisper.clean.txt" \
--model_name_or_path "<BART_MODEL_PATH>" \
--out ".\demo\rNxC16mlO60.summary.txt" \
--num_beams 6 \
--max_length 150 \
--min_length 50 \
--length_penalty 0.9 \
--device cpu \
--force
🧠 Model Choices
Whisper Small (CTranslate2)

Chosen for its balance between speed and transcription accuracy on CPU-only systems.
Using CTranslate2 significantly improves inference performance.

BART Large CNN

Used for abstractive summarization due to strong performance on long-form content like lectures and talks.

Chunked Summarization

BART supports ~1024 tokens per pass.
Long transcripts are split into chunks, summarized individually, then merged.

Transcript Cleaning

Normalization removes:

filler words

repeated fragments

spacing issues

ASR noise

Cleaner input improves summarization quality.

Lyric / Music Detection

Prevents poor summaries for songs or repetitive content.

📊 Example Output

Summary generated for the demo video:

George Hood set the world record for the longest plank in history. He kept going for an hour, for two hours, and then 10 hours. Hood said he kept his mind busy by focusing on conversations in the room.

Grit is not just willpower. It is strongly connected to biology, especially a protein called BDNF, which plays a role in memory and mental resilience.

Activities combining physical effort and concentration, such as yoga, have been shown to significantly increase BDNF levels.

Even short exercises like a one-minute plank can help build mental resilience.

⚠ Challenges & Solutions
Challenge	Reason	Solution
Whisper repetition	ASR artifacts	Transcript normalization
BART token limit	~1024 tokens	Chunk-based summarization
Poor summaries for songs	Repetitive lyrics	Lyric detection
Offline requirement	HF models download online	Local model snapshot
Multi-step pipeline	Hard to reproduce	PowerShell automation script
✅ Workflow Checklist

1️⃣ Activate virtual environment
2️⃣ Download YouTube audio
3️⃣ Transcribe using Whisper
4️⃣ Clean transcript
5️⃣ Run summarization
6️⃣ View final summary file

🧩 Final Notes

This project demonstrates a fully offline AI pipeline combining speech recognition and transformer-based summarization.

The architecture separates downloading, transcription, cleaning, and summarization into independent modules, following patterns commonly used in production ML systems.
