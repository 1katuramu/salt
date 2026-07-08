# Salt

Data tooling for the NSSF Searchbot, plus a standalone script for pulling down the Sunbird SALT dataset.

## What's in here

### `data/` — NSSF database setup and import tools

- **`schema.sql`** — Postgres schema for the searchbot: `nssf_members`, `contributions`, a joined `member_contributions_view`, indexes on the fields people actually search by (NSSF number, member name, employer, NIN), and triggers to keep `updated_at` current.
- **`import_script.py`** — CLI tool that reads an Excel export, cleans it up (fills missing values, parses dates, coerces numeric columns), and loads it into Postgres. Run it with:
  ```bash
  python import_script.py --excel-file path/to/export.xlsx --db-host localhost --db-name nssf_db --db-user nssf_user --db-password ***
  ```
- **`import_excel.py`** — same job as above but with a Tkinter GUI, for anyone who'd rather point-and-click a file picker than remember CLI flags.
- **`download_models.py`** — downloads a Whisper model (`tiny`/`base`/`small`/`medium`/`large`) for offline speech-to-text, used by the searchbot's voice search.
- **`hash_password.py`** — one-off utility for generating a bcrypt hash to drop into the searchbot's `config.yaml` auth file. Not meant to be run with real credentials committed anywhere.

### `db-sample-schemas/`

Oracle's public sample schemas repo, pulled in as a reference for schema and query patterns (customer orders, HR, order entry, sales history). Not code I wrote — kept here for reference while designing the NSSF schema.

### `salt.py`

Unrelated to the NSSF work — a script for pulling the [Sunbird SALT dataset](https://huggingface.co/datasets/Sunbird/salt) from Hugging Face. Downloads every config/split, saves each in Hugging Face's native format, and additionally dumps audio splits as `.wav` files with a `metadata.tsv` mapping filename to transcription. Useful for anyone experimenting with Ugandan language speech data.

```bash
python salt.py
```

Output lands in `sunbird_salt_all/<config>/<split>/`.

## Setup

```bash
pip install psycopg2-binary pandas sqlalchemy bcrypt openai-whisper datasets
```

(`tkinter` ships with most Python installs but may need a separate OS package on Linux, e.g. `sudo apt install python3-tk`.)

