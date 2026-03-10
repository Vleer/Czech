"""
Shared paths for Anki deck build. Use with a dataset name (e.g. example_sentences).

  data/<dataset>.csv           — input sentences (tab-separated: czech_word, english_translation, czech_sentence, english_sentence)
  output/<dataset>/cz_en.tsv   — Czech→English deck (no audio)
  output/<dataset>/cz_en_audio.tsv
  output/<dataset>/en_cz.tsv
  output/<dataset>/en_cz_audio.tsv
  output/<dataset>/audio/      — generated Czech TTS MP3s
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DATASET = "example_sentences"


def get_dataset() -> str:
    """Dataset name from argv[1] (e.g. when run as: python script.py <dataset>)."""
    return sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATASET


def data_dir() -> Path:
    return PROJECT_ROOT / "data"


def data_csv(dataset: str) -> Path:
    return data_dir() / f"{dataset}.csv"


def output_dir(dataset: str) -> Path:
    return PROJECT_ROOT / "output" / dataset


def cz_en_tsv(dataset: str) -> Path:
    return output_dir(dataset) / "cz_en.tsv"


def cz_en_audio_tsv(dataset: str) -> Path:
    return output_dir(dataset) / "cz_en_audio.tsv"


def en_cz_tsv(dataset: str) -> Path:
    return output_dir(dataset) / "en_cz.tsv"


def en_cz_audio_tsv(dataset: str) -> Path:
    return output_dir(dataset) / "en_cz_audio.tsv"


def audio_dir(dataset: str) -> Path:
    return output_dir(dataset) / "audio"
