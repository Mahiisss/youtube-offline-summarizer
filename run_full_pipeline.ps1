# param(
  # [string]$wavPath = ".\demo\input.wav",
  # [string]$whisperOut = ".\demo\input.whisper.txt",
  # [string]$cleanOut = ".\demo\input.whisper.clean.txt",
  # [string]$summaryOut = ".\demo\input.summary.txt",
# 
  # CHANGE this path to your local BART snapshot
  # [string]$bartSnapshot = "C:\Users\ritik\youtube-offline-summarizer\youtube-offline-summarizer\models\bart\models--facebook--bart-large-cnn\snapshots\37f520fa929c961707657b28798b30c003dd100b"
# )
# 
# Write-Output "=== Offline Summarization Pipeline Started ==="

# 1) Check WAV exists
# if (-not (Test-Path $wavPath)) {
  # Write-Error "❌ WAV not found: $wavPath"
  # exit 1
# }
# 
# 2) STT Whisper Transcription
# Write-Output "`n== Step 1: Transcribing audio with Whisper =="
# python src/stt_whisper.py --wav $wavPath --out $whisperOut --model small --device cpu
# if ($LASTEXITCODE -ne 0) { Write-Error "❌ Whisper transcription failed"; exit 2 }
# 
# 3) Transcript Cleaning
# Write-Output "`n== Step 2: Cleaning transcript =="
# python scripts/normalize_text.py $whisperOut $cleanOut
# if ($LASTEXITCODE -ne 0) { Write-Error "❌ Cleaning failed"; exit 3 }
# 
# 4) Summarizing with BART
# Write-Output "`n== Step 3: Summarizing with BART =="
# python src/summarize_text.py --transcript $cleanOut --model_name_or_path "$bartSnapshot" --out $summaryOut --num_beams 6 --max_length 180 --min_length 50 --length_penalty 0.9 --device cpu
# if ($LASTEXITCODE -ne 0) { Write-Error "❌ Summarizer failed"; exit 4 }
# 
# 5) Final Output
# Write-Output "`n== Step 4: Output Files in Demo Folder =="
# Get-ChildItem .\demo | Select-Object Name, Length, LastWriteTime
# 
# Write-Output "`n== Step 5: Summary Preview =="
# Get-Content $summaryOut -Raw | Select-Object -First 5
# 
# Write-Output "`n=== Pipeline Finished Successfully ==="
# 
# 
# & C:/Users/ritik/youtube-offline-summarizer/youtube-offline-summarizer/venv/Scripts/Activate.ps1
# .\run_full_pipeline.ps1 -wavPath ".\demo\H14bBuluwB8.wav"
# param(
  # [string]$wavPath       = ".\demo\input.wav",
  # [string]$whisperOut    = ".\demo\input.whisper.txt",
  # [string]$cleanOut      = ".\demo\input.whisper.clean.txt",
  # [string]$summaryOut    = ".\demo\input.src/summarize_text_improved.txt",
# 
  # CHANGE this to your local BART snapshot folder (the folder that contains config.json, tokenizer.json, model...)
  # [string]$bartSnapshot  = "C:\Users\ritik\youtube-offline-summarizer\youtube-offline-summarizer\models\bart\models--facebook--bart-large-cnn\snapshots\37f520fa929c961707657b28798b30c003dd100b",
# 
  # optional overrides
  # [string]$device        = "cpu",
  # [int]$num_beams        = 6,
  # [int]$max_length       = 180,
  # [int]$min_length       = 50,
  # [double]$length_penalty = 0.9,
  # [int]$chunk_words      = 400,
  # [switch]$force         # if present, force summarization even if music/lyrics detected
# )
# 
# Write-Output "=== Offline Summarization Pipeline Started ==="
# 
# 1) Check WAV exists
# if (-not (Test-Path $wavPath)) {
  # Write-Error "❌ WAV not found: $wavPath"
  # exit 1
# }
# 
# Activate venv note (optional): uncomment below if you want to auto-activate (path may differ)
# & .\venv\Scripts\Activate.ps1

# 2) STT Whisper Transcription
# Write-Output "`n== Step 1: Transcribing audio with Whisper =="
# Write-Output "Command: python src\stt_whisper.py --wav `"$wavPath`" --out `"$whisperOut`" --model small --device $device"
# python src\stt_whisper.py --wav $wavPath --out $whisperOut --model small --device $device
# if ($LASTEXITCODE -ne 0) { Write-Error "❌ Whisper transcription failed"; exit 2 }
# 
# 3) Transcript Cleaning / Normalization
# Write-Output "`n== Step 2: Cleaning transcript =="
# Write-Output "Command: python scripts\normalize_text.py `"$whisperOut`" `"$cleanOut`""
# python scripts\normalize_text.py $whisperOut $cleanOut
# if ($LASTEXITCODE -ne 0) { Write-Error "❌ Cleaning failed"; exit 3 }
# 
# 4) Summarizing with BART (improved)
# Write-Output "`n== Step 3: Summarizing with BART =="
# $forceFlag = ""
# if ($force.IsPresent) { $forceFlag = "--force" }
# Write-Output "Command: python src\summarize_text_improved.py --transcript `"$cleanOut`" --model_name_or_path `"$bartSnapshot`" --out `"$summaryOut`" --num_beams $num_beams --max_length $max_length --min_length $min_length --length_penalty $length_penalty --device $device --chunk_words $chunk_words $forceFlag"
# python src\summarize_text_improved.py --transcript $cleanOut --model_name_or_path "$bartSnapshot" --out $summaryOut --num_beams $num_beams --max_length $max_length --min_length $min_length --length_penalty $length_penalty --device $device --chunk_words $chunk_words $forceFlag
# if ($LASTEXITCODE -ne 0) { Write-Error "❌ Summarizer failed"; exit 4 }
# 
# 5) Final Output
# Write-Output "`n== Step 4: Output files in demo/ =="
# Get-ChildItem .\demo | Select-Object Name, Length, LastWriteTime
# 
# Write-Output "`n== Step 5: Summary preview =="
# if (Test-Path $summaryOut) {
  # Get-Content $summaryOut -Raw | Select-Object -First 10
# } else {
  # Write-Output "Summary file not found: $summaryOut"
# }
# 
# Write-Output "`n=== Pipeline Finished Successfully ==="
param(
  [string]$wavPath = ".\demo\input.wav",
  [string]$outDir = ".\demo",
  [string]$bartSnapshot = "C:\Users\ritik\youtube-offline-summarizer\youtube-offline-summarizer\models\bart\models--facebook--bart-large-cnn\snapshots\37f520fa929c961707657b28798b30c003dd100b"
)

Write-Output "=== Offline Summarization Pipeline Started ==="

# ensure venv activated before running this script (or run from already-activated PS)
# 1) Check WAV exists
if (-not (Test-Path $wavPath)) {
  Write-Error "❌ WAV not found: $wavPath"
  exit 1
}

# derive base name and paths
$base = [IO.Path]::GetFileNameWithoutExtension($wavPath)
$whisperOut = Join-Path $outDir ($base + ".whisper.txt")
$cleanOut   = Join-Path $outDir ($base + ".whisper.clean.txt")
$summaryOut = Join-Path $outDir ($base + ".summary.txt")

Write-Output "`n== Step 1: Transcribing audio with Whisper =="
Write-Output "Command: python src\stt_whisper.py --wav `"$wavPath`" --out `"$whisperOut`" --model small --device cpu"
python src\stt_whisper.py --wav $wavPath --out $whisperOut --model small --device cpu
if ($LASTEXITCODE -ne 0) { Write-Error "❌ Whisper transcription failed"; exit 2 }

Write-Output "`n== Step 2: Cleaning transcript =="
Write-Output "Command: python scripts\normalize_text.py `"$whisperOut`" `"$cleanOut`""
python scripts\normalize_text.py $whisperOut $cleanOut
if ($LASTEXITCODE -ne 0) { Write-Error "❌ Cleaning failed"; exit 3 }

Write-Output "`n== Step 3: Summarizing with BART =="
# call improved summarizer (force not used by default)
$cmd = "python src\summarize_text_improved.py --transcript `"$cleanOut`" --model_name_or_path `"$bartSnapshot`" --out `"$summaryOut`" --num_beams 6 --max_length 180 --min_length 50 --length_penalty 0.9 --device cpu --chunk_words 400"
Write-Output "Command: $cmd"
Invoke-Expression $cmd
if ($LASTEXITCODE -ne 0) { Write-Error "❌ Summarizer failed"; exit 4 }

Write-Output "`n== Step 4: Output Files in Demo Folder =="
Get-ChildItem $outDir | Select-Object Name, Length, LastWriteTime

Write-Output "`n== Step 5: Summary Preview =="
Get-Content $summaryOut -Raw | Select-Object -First 5

Write-Output "`n=== Pipeline Finished Successfully ==="
