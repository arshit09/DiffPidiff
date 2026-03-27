# DiffPidiff

A simple tool to compare two PDF files and generate a highlighted diff report as a new PDF.

- **Green** — added text
- **Red with strikethrough** — removed text
- **Black** — unchanged text

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### GUI mode (default)

```bash
python pdf_diff.py
```

File dialogs will prompt you to select the original PDF, the modified PDF, and the output location.

### CLI mode

```bash
python pdf_diff.py original.pdf modified.pdf -o diff_report.pdf
```

| Argument | Description |
|----------|-------------|
| `original.pdf` | Path to the original (old) PDF |
| `modified.pdf` | Path to the modified (new) PDF |
| `-o`, `--output` | Output path for the diff report (default: `diff_report.pdf`) |

## How it works

1. Extracts text from each PDF using PyMuPDF
2. Computes a line-level diff using Python's `difflib.SequenceMatcher`
3. Generates a styled PDF report using ReportLab with color-coded additions and removals

## Requirements

- Python 3.10+
- [PyMuPDF](https://pymupdf.readthedocs.io/) — PDF text extraction
- [ReportLab](https://www.reportlab.com/) — PDF generation

## License

MIT License. See [LICENSE](LICENSE) for details.
