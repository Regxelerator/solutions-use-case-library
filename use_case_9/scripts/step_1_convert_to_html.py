import os
import subprocess


def convert_pdf_to_html(pdf_to_html_exe_path: str, pdf_path: str, html_path: str):
    """
    Converts a PDF to HTML.
    Args:
        pdf_to_html_exe_path: pdf_to_html_exe utility path
        pdf_path: Annual report path
        html_path: Path to save HTML.

    Returns:
        None
    """
    with open(os.devnull, "w") as FNULL:
        subprocess.run(
            [
                pdf_to_html_exe_path,
                "-s",
                "-i",
                "-nodrm",
                "-hidden",
                "-noframes",
                pdf_path,
                html_path,
            ],
            stdout=FNULL,
            stderr=FNULL,
            check=True,
        )


def convert_save_pdf_to_html(
    pdf_to_html_exe_path, annual_report_dir: str, html_output_dir: str
) -> None:
    """
    Method converts a PDF to HTML.
    """
    for filename in os.listdir(annual_report_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(annual_report_dir, filename)
            base_name = os.path.splitext(filename)[0]
            html_path = os.path.join(html_output_dir, f"{base_name}.html")
            if not os.path.isfile(pdf_path):
                print(f"{base_name} File not found: {pdf_path}")
                continue
            try:
                convert_pdf_to_html(pdf_to_html_exe_path, pdf_path, html_path)
                print(f"Converted: {filename} -> {html_output_dir}")
            except Exception as e:
                print(f"Error converting {filename}: {e}")
