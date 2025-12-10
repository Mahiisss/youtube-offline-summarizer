import re
import sys
from pathlib import Path

def clean_transcript(input_path, output_path):
    text = Path(input_path).read_text(encoding="utf-8")

    # Remove all timestamp patterns like: 12.34 --> 56.78
    text = re.sub(r"\d+\.\d+\s*-->\s*\d+\.\d+", "", text)

    # Remove standalone timestamps like "0.00" or "19.12"
    text = re.sub(r"\b\d+\.\d+\b", "", text)

    # Remove extra newlines and spaces
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r" +", " ", text).strip()

    Path(output_path).write_text(text, encoding="utf-8")
    print(f"Cleaned transcript written to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python normalize_text.py input.txt output.txt")
        sys.exit(1)

    clean_transcript(sys.argv[1], sys.argv[2])



