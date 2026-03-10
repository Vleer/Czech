"""
English → Czech deck: Front = English word + example sentence, Back = Czech word + example.

Reads data/<dataset>.csv, writes output/<dataset>/en_cz.tsv.
Usage: python make_anki_cards_en_cz.py [dataset]
Default dataset: example_sentences
"""
import csv
import re
from pathlib import Path
from urllib.parse import quote_plus

import paths

DATASET = paths.get_dataset()
INPUT_PATH = paths.data_csv(DATASET)
OUTPUT_PATH = paths.en_cz_tsv(DATASET)


def highlight_word_in_sentence(word: str, sentence: str) -> str:
    """Wrap the first standalone occurrence of `word` in the sentence in a blue span."""
    pattern = r"\b{}\b".format(re.escape(word))

    def _repl(match: re.Match) -> str:
        text = match.group(0)
        return f'<span style="color:#06c; font-weight:bold;">{text}</span>'

    return re.sub(pattern, _repl, sentence, count=1, flags=re.IGNORECASE)


def main() -> None:
    if not INPUT_PATH.exists():
        raise SystemExit(f"Input file not found: {INPUT_PATH}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with INPUT_PATH.open("r", encoding="utf-8", newline="") as infile, OUTPUT_PATH.open(
        "w", encoding="utf-8", newline=""
    ) as outfile:
        reader = csv.DictReader(infile, delimiter="\t")
        writer = csv.writer(outfile, delimiter="\t")

        for row in reader:
            czech_word = (row.get("czech_word") or "").strip()
            english_translation = (row.get("english_translation") or "").strip()
            czech_sentence = (row.get("czech_sentence") or "").strip()
            english_sentence = (row.get("english_sentence") or "").strip()

            if not (czech_word and english_translation and czech_sentence and english_sentence):
                continue

            highlighted_english_sentence = highlight_word_in_sentence(english_translation, english_sentence)
            highlighted_czech_sentence = highlight_word_in_sentence(czech_word, czech_sentence)

            query = f"Explain what this sentence means in simple terms. Break down grammatical concepts: {czech_sentence}"
            perplexity_url = "https://www.perplexity.ai/search?q=" + quote_plus(query)

            front = (
                f"{english_translation}<br><br>"
                f"{highlighted_english_sentence}"
            )
            back = (
                f'{czech_word}<br><br>'
                f'<a href="{perplexity_url}" target="_blank" '
                f'style="color: inherit; text-decoration: none;">'
                f'{highlighted_czech_sentence}</a>'
            )

            writer.writerow([front, back])

    print(f"Wrote English->Czech cards to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
