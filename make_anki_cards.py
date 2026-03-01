import csv
from pathlib import Path
import re
from urllib.parse import quote_plus

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
            # Some rows (e.g. blank lines) may produce None values; guard against that
            czech_word = (row.get("czech_word") or "").strip()
            english_translation = (row.get("english_translation") or "").strip()
            czech_sentence = (row.get("czech_sentence") or "").strip()
            english_sentence = (row.get("english_sentence") or "").strip()

            # Skip rows that don't have all required fields populated
            if not (czech_word and english_translation and czech_sentence and english_sentence):
                continue

            highlighted_czech_sentence = highlight_word_in_sentence(czech_word, czech_sentence)
            highlighted_english_sentence = highlight_word_in_sentence(english_translation, english_sentence)

            query = f"Explain what this sentence means in simple terms. Break down grammatical concepts: {czech_sentence}"
            perplexity_url = "https://www.perplexity.ai/search?q=" + quote_plus(query)

            # Anki Basic note: Front, Back
            # Front: tested word + Czech example (with highlighted word)
            # Back: English translation + English example (with highlighted word)
            # The anchor is styled to look like normal text (no underline/link color).
            front = (
                f'{czech_word}<br><br>'
                f'<a href="{perplexity_url}" target="_blank" '
                f'style="color: inherit; text-decoration: none;">'
                f'{highlighted_czech_sentence}</a>'
            )
            back = (
                f"{english_translation}<br><br>"
                f"{highlighted_english_sentence}"
            )

            writer.writerow([front, back])

    print(f"Wrote Anki cards to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
