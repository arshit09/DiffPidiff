"""
PDF Diff Tool
Select two PDFs, compare them, and generate a highlighted diff PDF.
Green = added text, Red with strikethrough = removed text, Black = unchanged.
"""

import argparse
import difflib
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF is required. Install it with: pip install PyMuPDF")
    sys.exit(1)

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
except ImportError:
    print("reportlab is required. Install it with: pip install reportlab")
    sys.exit(1)


def extract_text_by_page(pdf_path: str) -> list[str]:
    """Extract text from each page of a PDF."""
    doc = fitz.open(pdf_path)
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return pages


def select_pdfs() -> tuple[str, str]:
    """Open file dialogs to select two PDFs."""
    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo("PDF Diff Tool", "Select the ORIGINAL (old) PDF file.")
    pdf1 = filedialog.askopenfilename(
        title="Select Original PDF",
        filetypes=[("PDF files", "*.pdf")],
    )
    if not pdf1:
        messagebox.showerror("Error", "No file selected. Exiting.")
        sys.exit(1)

    messagebox.showinfo("PDF Diff Tool", "Now select the MODIFIED (new) PDF file.")
    pdf2 = filedialog.askopenfilename(
        title="Select Modified PDF",
        filetypes=[("PDF files", "*.pdf")],
    )
    if not pdf2:
        messagebox.showerror("Error", "No file selected. Exiting.")
        sys.exit(1)

    root.destroy()
    return pdf1, pdf2


def compute_diff(old_lines: list[str], new_lines: list[str]) -> list[tuple[str, str]]:
    """
    Compare old and new lines, return list of (tag, text) tuples.
    tag is one of: 'equal', 'added', 'removed'.
    """
    result = []
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)

    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            for line in old_lines[i1:i2]:
                result.append(("equal", line))
        elif op == "replace":
            for line in old_lines[i1:i2]:
                result.append(("removed", line))
            for line in new_lines[j1:j2]:
                result.append(("added", line))
        elif op == "delete":
            for line in old_lines[i1:i2]:
                result.append(("removed", line))
        elif op == "insert":
            for line in new_lines[j1:j2]:
                result.append(("added", line))

    return result


def escape_xml(text: str) -> str:
    """Escape special XML characters for ReportLab paragraphs."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def generate_diff_pdf(diff_data: list[tuple[str, str]], output_path: str):
    """Generate a PDF with colored highlights for additions and removals."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()

    style_equal = ParagraphStyle(
        "Equal",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor="black",
        spaceAfter=2,
    )
    style_added = ParagraphStyle(
        "Added",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor="green",
        backColor="#e6ffe6",
        spaceAfter=2,
        leftIndent=10,
        borderWidth=0.5,
        borderColor="green",
        borderPadding=3,
    )
    style_removed = ParagraphStyle(
        "Removed",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor="red",
        backColor="#ffe6e6",
        spaceAfter=2,
        leftIndent=10,
        borderWidth=0.5,
        borderColor="red",
        borderPadding=3,
    )

    # Title styles
    title_style = ParagraphStyle(
        "DiffTitle",
        parent=styles["Title"],
        fontSize=16,
        spaceAfter=12,
    )
    legend_style = ParagraphStyle(
        "Legend",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=20,
    )

    story = []

    # Title
    story.append(Paragraph("PDF Diff Report", title_style))
    story.append(
        Paragraph(
            '<font color="green">\u2588 Green = Added</font> &nbsp;&nbsp; '
            '<font color="red">\u2588 Red = Removed</font> &nbsp;&nbsp; '
            '<font color="black">\u2588 Black = Unchanged</font>',
            legend_style,
        )
    )
    story.append(Spacer(1, 12))

    # Build paragraphs from diff
    for tag, text in diff_data:
        text = text.strip()
        if not text:
            continue

        escaped = escape_xml(text)

        if tag == "equal":
            story.append(Paragraph(escaped, style_equal))
        elif tag == "added":
            story.append(
                Paragraph(f"<b>[+]</b> {escaped}", style_added)
            )
        elif tag == "removed":
            story.append(
                Paragraph(f"<b>[\u2013]</b> <strike>{escaped}</strike>", style_removed)
            )

    if not story:
        story.append(Paragraph("No differences found.", styles["Normal"]))

    doc.build(story)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Compare two PDFs and generate a highlighted diff report.",
    )
    parser.add_argument("original", nargs="?", help="Path to the original (old) PDF")
    parser.add_argument("modified", nargs="?", help="Path to the modified (new) PDF")
    parser.add_argument(
        "-o", "--output", default="diff_report.pdf", help="Output path (default: diff_report.pdf)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    cli_mode = args.original and args.modified

    print("PDF Diff Tool")
    print("=" * 40)

    # Step 1: Select PDFs
    if cli_mode:
        pdf1_path, pdf2_path = args.original, args.modified
    else:
        pdf1_path, pdf2_path = select_pdfs()

    print(f"Original: {pdf1_path}")
    print(f"Modified: {pdf2_path}")

    # Step 2: Extract text
    print("Extracting text from PDFs...")
    old_pages = extract_text_by_page(pdf1_path)
    new_pages = extract_text_by_page(pdf2_path)

    old_text = "\n".join(old_pages)
    new_text = "\n".join(new_pages)

    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()

    # Step 3: Compute diff
    print("Computing differences...")
    diff_data = compute_diff(old_lines, new_lines)

    # Stats
    added = sum(1 for tag, _ in diff_data if tag == "added")
    removed = sum(1 for tag, _ in diff_data if tag == "removed")
    unchanged = sum(1 for tag, _ in diff_data if tag == "equal")
    print(f"  Added:     {added} lines")
    print(f"  Removed:   {removed} lines")
    print(f"  Unchanged: {unchanged} lines")

    # Step 4: Choose output path
    if cli_mode:
        output_path = args.output
    else:
        root = tk.Tk()
        root.withdraw()
        output_path = filedialog.asksaveasfilename(
            title="Save Diff PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="diff_report.pdf",
        )
        root.destroy()
        if not output_path:
            print("No output file selected. Exiting.")
            sys.exit(1)

    # Step 5: Generate output PDF
    print(f"Generating diff PDF: {output_path}")
    generate_diff_pdf(diff_data, output_path)
    print("Done! Diff PDF generated successfully.")


if __name__ == "__main__":
    main()
