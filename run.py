#!/usr/bin/env python3
"""Create/use a venv and run deck build scripts. Data: data/<dataset>.csv → output/<dataset>/

  python run.py                     → full build (make_cards + add_audio) for example_sentences
  python run.py <dataset>           → full build for that dataset (e.g. python run.py example_sentences)
  python run.py make_cards [dataset]
  python run.py add_audio [dataset]
  python run.py make_cards_en_cz [dataset]
  python run.py add_audio_en_cz [dataset]
"""
import os
import subprocess
import sys
from pathlib import Path

VENV_DIR = Path(__file__).resolve().parent / ".venv"
REQUIREMENTS = Path(__file__).resolve().parent / "requirements.txt"
SCRIPTS = {
    "make_cards": Path(__file__).resolve().parent / "make_anki_cards.py",
    "add_audio": Path(__file__).resolve().parent / "add_audio.py",
    "make_cards_en_cz": Path(__file__).resolve().parent / "make_anki_cards_en_cz.py",
    "add_audio_en_cz": Path(__file__).resolve().parent / "add_audio_en_cz.py",
}
DEFAULT_DATASET = "example_sentences"


def parse_args():
    """Return (command or None for full build, dataset name)."""
    argv = sys.argv[1:]
    if not argv:
        return None, DEFAULT_DATASET
    if argv[0] in SCRIPTS:
        cmd = argv[0]
        dataset = argv[1] if len(argv) > 1 else DEFAULT_DATASET
        return cmd, dataset
    # First arg is dataset name → full build
    return None, argv[0]


def main() -> None:
    if not VENV_DIR.exists():
        print("Creating virtual environment at .venv ...")
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])

    if sys.prefix != str(VENV_DIR.resolve()):
        python = VENV_DIR / "Scripts" / "python.exe" if os.name == "nt" else VENV_DIR / "bin" / "python"
        if not python.exists():
            python = VENV_DIR / "bin" / "python3"
        subprocess.check_call([str(python), __file__] + sys.argv[1:])
        return

    cmd, dataset = parse_args()

    if cmd is None:
        # Full build: make_cards then add_audio
        if REQUIREMENTS.exists():
            print("Installing requirements ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", str(REQUIREMENTS)])
        for key in ("make_cards", "add_audio"):
            script = SCRIPTS[key]
            print(f"Running {script.name} ({dataset}) ...")
            subprocess.check_call([sys.executable, str(script), dataset])
        return

    script = SCRIPTS.get(cmd)
    if not script.exists():
        raise SystemExit(f"Script not found: {script}")

    if cmd in ("add_audio", "add_audio_en_cz") and REQUIREMENTS.exists():
        print("Installing requirements ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", str(REQUIREMENTS)])

    print(f"Running {script.name} ({dataset}) ...")
    subprocess.check_call([sys.executable, str(script), dataset])


if __name__ == "__main__":
    main()
