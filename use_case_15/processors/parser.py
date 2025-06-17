import os
import fitz

from utils.utils import write_into_markdown_file

class DocumentParser:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir


    def is_scanned_pdf(self, file_path: str) -> str:
        """
        Determine whether a PDF is text-based, scanned, or mixed.
        """
        doc = fitz.open(file_path)
        for page in doc:
            if page.get_text().strip():
                if page.get_images(full=True):
                    return "mixed"

        if any(page.get_text().strip() for page in doc):
            return "text_based"
        elif any(page.get_images(full=True) for page in doc):
            return "scanned"
        return ""


    def _process_file(self, file_path, count, relative_path=""):
        filename = os.path.basename(file_path)
        reader = self.get_reader(file_path)
        ext = os.path.splitext(file_path)[1].lower()

        if not reader:
            return False

        print(
            f"\n--- Processing file no.{count} -- "
            f"`{relative_path + '/' if relative_path else ''}{filename}` ---"
        )

        if ext == ".pdf":
            pdf_type = self.is_scanned_pdf(file_path)
            if pdf_type == "text_based":
                print("\nThe PDF document is text-based – extracting text...")
                text = reader.extract_text()
            elif pdf_type == "scanned":
                print("\nThe PDF document is scanned – extracting text from images...")
                text = reader.extract_images(method="ocr")
            elif pdf_type == "mixed":
                print(
                    "\nThe PDF document contains both text and images – "
                    "extracting text and images..."
                )
                text1 = reader.extract_text()
                text = reader.extract_scanned_images(self.output_dir, text1)
            else:
                print("\nThe PDF document is empty or unreadable.")
                text = ""

        elif ext in [".jpg", ".jpeg", ".png"]:
            print("\nProcessing image file – extracting text using OCR...")
            text = reader.extract_text()
            tables = reader.extract_tables()
            if tables:
                text += "\n\n### Detected Tables:\n"
                for i, table in enumerate(tables, 1):
                    text += f"\nTable {i}:\n"
                    for row in table:
                        text += " | ".join(row) + "\n"

        elif ext in [".docx", ".odt"]:
            print("\nExtracting text from document...")
            text = reader.extract_text()
            tables = reader.extract_tables()
            if tables:
                text += "\n\n### Tables:\n"
                for i, table in enumerate(tables, 1):
                    text += f"\nTable {i}:\n"
                    for row in table:
                        text += " | ".join(str(cell) for cell in row) + "\n"

        elif ext == ".pptx":  
            print("\nExtracting text from PowerPoint file...")
            text = reader.extract_text()
            tables = reader.extract_tables()
            if tables:
                text += "\n\n### Tables:\n"
                for i, table in enumerate(tables, 1):
                    text += f"\nTable {i}:\n"
                    for row in table:
                        text += " | ".join(str(cell) for cell in row) + "\n"

        elif ext == ".xlsx":
            print("\nExtracting content from Excel file...")
            text = reader.extract_text()
            tables = reader.extract_tables()
            if tables:
                text += "\n\n### Sheets and Tables:\n"
                for i, table in enumerate(tables, 1):
                    text += f"\nSheet/Table {i}:\n"
                    for row in table:
                        text += " | ".join(str(cell) for cell in row) + "\n"

        else:
            print("\nExtracting content from file...")
            text = reader.extract_text()

        output_subdir = (
            os.path.join(self.output_dir, relative_path)
            if relative_path
            else self.output_dir
        )
        os.makedirs(output_subdir, exist_ok=True)

        md_file_name = os.path.splitext(os.path.splitext(filename)[0])[0]
        md_file = os.path.join(output_subdir, f"{md_file_name}.md")

        status = write_into_markdown_file(md_file, text)
        if status:
            print("Document successfully converted to Markdown format.")
            print(f"File saved at: {md_file}")
        else:
            print(f"Failed to write the document to {md_file}.")

        return True

    def process_all_files(self):
        """
        Walk the input directory and process every file,
        preserving the directory structure in the output directory.
        """
        count = 1
        processed = 0

        for root, _, files in os.walk(self.input_dir):
            files = [f for f in files if not f.startswith("~$")]  
            relative_path = os.path.relpath(root, self.input_dir)
            relative_path = "" if relative_path == "." else relative_path

            for filename in files:
                file_path = os.path.join(root, filename)
                if self._process_file(file_path, count, relative_path):
                    processed += 1
                count += 1

        if processed == 0:
            print("No files found in the input directory to process.")
            print("Please place files into input directory and try again.")