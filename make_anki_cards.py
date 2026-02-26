import csv
from pathlib import Path
import re

INPUT_PATH = Path("example_sentences.csv")
OUTPUT_PATH = Path("anki_example_sentences.tsv")


def highlight_word_in_sentence(word: str, sentence: str) -> str:
    """Wrap the first standalone occurrence of `word` in the sentence in a blue span.

    Uses a word-boundary regex so we don't color inside longer words.
    The match is case-insensitive so capitalized forms are also caught.
    """
    pattern = r"\b{}\b".format(re.escape(word))

    def _repl(match: re.Match) -> str:
        text = match.group(0)
        return f'<span style="color:#06c; font-weight:bold;">{text}</span>'

    return re.sub(pattern, _repl, sentence, count=1, flags=re.IGNORECASE)


def main() -> None:
    if not INPUT_PATH.exists():
        raise SystemExit(f"Input file not found: {INPUT_PATH}")

    with INPUT_PATH.open("r", encoding="utf-8", newline="") as infile, OUTPUT_PATH.open(
        "w", encoding="utf-8", newline=""
    ) as outfile:
        reader = csv.DictReader(infile, delimiter="\t")
        writer = csv.writer(outfile, delimiter="\t")

        # No header row in output: every line is a card (Front, Back)
        for row in reader:
            czech_word = row["czech_word"].strip()
            english_translation = row["english_translation"].strip()
            czech_sentence = row["czech_sentence"].strip()
            english_sentence = row["english_sentence"].strip()

            highlighted_czech_sentence = highlight_word_in_sentence(czech_word, czech_sentence)
            highlighted_english_sentence = highlight_word_in_sentence(english_translation, english_sentence)

            # Anki Basic note: Front, Back
            # Front: tested word + Czech example (with highlighted word)
            # Back: English translation + English example (with highlighted word)
            front = f"{czech_word}<br><br>{highlighted_czech_sentence}"
            back = (
                f"{english_translation}<br><br>"
                f"{highlighted_english_sentence}"
            )

            writer.writerow([front, back])

    print(f"Wrote Anki cards to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
