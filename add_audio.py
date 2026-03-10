"""
Add Czech TTS to the Czech→English deck. Injects [sound:...] into the front (Czech side).

Run after make_anki_cards.py. Reads data/<dataset>.csv and output/<dataset>/cz_en.tsv;
writes output/<dataset>/cz_en_audio.tsv and output/<dataset>/audio/.
Usage: python add_audio.py [dataset]
"""
import asyncio
import csv
import hashlib
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Optional

import edge_tts
import paths

DATASET = paths.get_dataset()
INPUT_CSV = paths.data_csv(DATASET)
INPUT_TSV = paths.cz_en_tsv(DATASET)
OUTPUT_TSV = paths.cz_en_audio_tsv(DATASET)
AUDIO_DIR = paths.audio_dir(DATASET)
CZECH_VOICE = "cs-CZ-AntoninNeural"
RATE = "-20%"


def _audio_filename(czech_sentence: str) -> str:
    h = hashlib.sha256(czech_sentence.encode("utf-8")).hexdigest()[:12]
    return f"{h}.mp3"


async def ensure_czech_audio(czech_sentence: str, audio_dir: Path) -> str:
    audio_dir.mkdir(parents=True, exist_ok=True)
    name = _audio_filename(czech_sentence)
    path = audio_dir / name
    if path.exists():
        return name
    communicate = edge_tts.Communicate(czech_sentence, CZECH_VOICE, rate=RATE)
    await communicate.save(str(path))
    return name


def _anki_media_folder() -> Optional[Path]:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", "")) / "Anki2"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / "Anki2"
    else:
        base = Path.home() / ".local" / "share" / "Anki2"
    if not base.is_dir():
        return None
    for p in base.iterdir():
        if p.is_dir() and not p.name.startswith("."):
            media = p / "collection.media"
            if media.is_dir():
                return media
    return None


def _copy_audio_to_anki(audio_dir: Path) -> bool:
    dest = _anki_media_folder()
    if dest is None:
        return False
    count = 0
    for f in audio_dir.glob("*.mp3"):
        shutil.copy2(f, dest / f.name)
        count += 1
    if count:
        print(f"Copied {count} audio file(s) to Anki media folder:\n  {dest}")
    return count > 0


def _inject_sound(front: str, audio_name: str) -> str:
    sound_tag = f"[sound:{audio_name}]"
    if "[sound:" in front:
        front = re.sub(r"\[sound:[^\]]+\.mp3\]\s*(?:<br><br>)?", "", front)
    marker = "<br><br>"
    idx = front.find(marker)
    if idx == -1:
        return f"{sound_tag}<br><br>{front}"
    insert_at = idx + len(marker)
    return front[:insert_at] + f"{sound_tag}<br><br>" + front[insert_at:]


async def main() -> None:
    if not INPUT_CSV.exists():
        raise SystemExit(f"Input CSV not found: {INPUT_CSV}")
    if not INPUT_TSV.exists():
        raise SystemExit(f"Input TSV not found: {INPUT_TSV}. Run make_anki_cards.py first.")

    rows: list[dict[str, str]] = []
    with INPUT_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            czech_sentence = (row.get("czech_sentence") or "").strip()
            czech_word = (row.get("czech_word") or "").strip()
            english_translation = (row.get("english_translation") or "").strip()
            english_sentence = (row.get("english_sentence") or "").strip()
            if not (czech_word and english_translation and czech_sentence and english_sentence):
                continue
            rows.append({"czech_sentence": czech_sentence})

    unique_sentences = list({r["czech_sentence"] for r in rows})
    print(f"Generating TTS for {len(unique_sentences)} Czech example sentences...")
    sentence_to_audio: dict[str, str] = {}
    for sent in unique_sentences:
        name = await ensure_czech_audio(sent, AUDIO_DIR)
        sentence_to_audio[sent] = name

    tsv_rows: list[tuple[str, str]] = []
    with INPUT_TSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        for line in reader:
            if len(line) >= 2:
                tsv_rows.append((line[0], line[1]))
            elif len(line) == 1:
                tsv_rows.append((line[0], ""))

    n_match = min(len(tsv_rows), len(rows))
    if n_match < len(tsv_rows):
        print(f"Note: TSV has {len(tsv_rows)} cards, CSV has {len(rows)}. Adding audio to first {n_match}.")

    with OUTPUT_TSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        for i, (front, back) in enumerate(tsv_rows):
            if i < len(rows):
                audio_name = sentence_to_audio[rows[i]["czech_sentence"]]
                front = _inject_sound(front, audio_name)
            writer.writerow([front, back])

    print(f"Wrote deck with audio to {OUTPUT_TSV}")

    if not _copy_audio_to_anki(AUDIO_DIR):
        print(
            "Anki does not load media from the TSV directory. Copy all .mp3 from\n"
            f"  {AUDIO_DIR}\n"
            "into your Anki media folder (%APPDATA%\\Anki2\\<Profile>\\collection.media),\n"
            "then run Tools → Check Media in Anki."
        )


if __name__ == "__main__":
    asyncio.run(main())
