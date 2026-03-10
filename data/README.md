# Input data (one CSV per dataset)

Put tab-separated CSV files here. Each file becomes a **dataset**; use its name (without `.csv`) when building.

- **example_sentences** (default): `data/example_sentences.csv`  
  Build: `python run.py` or `python run.py example_sentences`

To add another set (e.g. `data/my_set.csv`), run: `python run.py my_set`

## CSV format

Header row (tab-separated):

```
czech_word	english_translation	czech_sentence	english_sentence
```

One row per note. Rows missing any of these columns are skipped.
