import os
import pandas as pd
from datetime import datetime
from collections import defaultdict
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from utils.file_handler import load_json


def set_run_font(run, font_name="Calibri", font_size=10, is_bold=False):
    """
    Sets the font style for a given text run in a Word document.

    Args:
        run: A `Run` object from `python-docx` representing a segment of text.
        font_name (str, optional): The name of the font to apply. Defaults to "Calibri".
        font_size (int, optional): The font size in points. Defaults to 10.
        is_bold (bool, optional): Whether the text should be bold. Defaults to False.
    """
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.font.bold = is_bold
    run.font.color.rgb = RGBColor(0, 0, 0)


def set_heading_run_font(run, font_name="Calibri Light", font_size=14, is_bold=True):
    """
    Sets the font style for a heading run in a Word document.

    Args:
        run: A `Run` object from `python-docx` representing a heading text segment.
        font_name (str, optional): The name of the font to apply. Defaults to "Calibri Light".
        font_size (int, optional): The font size in points. Defaults to 14.
        is_bold (bool, optional): Whether the heading should be bold. Defaults to True.
    """
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.font.bold = is_bold
    run.font.color.rgb = RGBColor(0, 0, 0)


def insert_table_of_contents(doc):
    """
    Inserts a Table of Contents (ToC) into a Word document.

    Args:
        doc: A `Document` object from `python-docx` representing the Word document.
    """
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()

    fldChar_begin = OxmlElement("w:fldChar")
    fldChar_begin.set(qn("w:fldCharType"), "begin")

    fldChar_separate = OxmlElement("w:fldChar")
    fldChar_separate.set(qn("w:fldCharType"), "separate")

    fldChar_end = OxmlElement("w:fldChar")
    fldChar_end.set(qn("w:fldCharType"), "end")

    run._r.append(fldChar_begin)
    run._r.append(fldChar_separate)
    run._r.append(fldChar_end)


def create_footer_disclaimer_and_page_number(section):
    """
    Adds a footer to a Word document section with a disclaimer and page number.

    Args:
        section: A `Section` object from `python-docx` representing the document section.
    """
    footer = section.footer
    footer.paragraphs.clear()

    para_left = footer.add_paragraph()
    para_left.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run_left = para_left.add_run(
        "Disclaimer: This output was created through the application of generative AI. "
        "Please validate accuracy and completeness before using it for decision-making."
    )
    set_run_font(run_left, font_size=8, font_name="Calibri")

    para_right = footer.add_paragraph()
    para_right.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    run_right = para_right.add_run()
    fldChar_begin = OxmlElement("w:fldChar")
    fldChar_begin.set(qn("w:fldCharType"), "begin")

    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = "PAGE"

    fldChar_separate = OxmlElement("w:fldChar")
    fldChar_separate.set(qn("w:fldCharType"), "separate")

    fldChar_end = OxmlElement("w:fldChar")
    fldChar_end.set(qn("w:fldCharType"), "end")

    run_right._r.append(fldChar_begin)
    run_right._r.append(instrText)
    run_right._r.append(fldChar_separate)
    run_right._r.append(fldChar_end)

    set_run_font(run_right, font_size=8, font_name="Calibri")


def sort_key(ch):
    """
    Converts a string to an integer if possible, otherwise assigns a high default value.

    Args:
        ch: A string representing a potential number.

    Returns:
        int: The integer representation of the string if conversion succeeds; otherwise, returns a large default value (999999).

    """
    try:
        return int(ch)
    except ValueError:
        return 999999


def main_word(
    conult_quest_summary_json: str,
    consult_paper_info_json: str,
    executive_summary_json: str,
    output_dir: str,
) -> None:
    """
    Generates a Word document summarizing consultation questions and responses.

    Args:
        conult_quest_summary_json (str): Path to consultation question summaries JSON file.
        consult_paper_info_json (str): Path to consultation paper information JSON file.
        executive_summary_json (str): Path to executive summary JSON file.
        output_dir (str): Directory path where the Word document will be saved.
    """
    summaries = load_json(conult_quest_summary_json)
    consultation_paper = load_json(consult_paper_info_json)
    executive_summary_data = load_json(executive_summary_json)

    consultation_title = consultation_paper.get("General_Information", {}).get(
        "Consultation_Title", "Untitled Consultation"
    )

    chapters_map = defaultdict(list)
    for item in summaries:
        chap_id = item["chapter_id"]
        chapters_map[chap_id].append(item)

    sorted_chapters = sorted(chapters_map.keys(), key=sort_key)

    doc = Document()
    section = doc.sections[0]
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.top_margin = Inches(3)
    section.bottom_margin = Inches(3)

    create_footer_disclaimer_and_page_number(section)

    title_par_1 = doc.add_paragraph()
    title_par_1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title_1 = title_par_1.add_run("Summary Report")
    set_heading_run_font(
        run_title_1, font_size=28, font_name="Calibri Light", is_bold=True
    )

    title_par_2 = doc.add_paragraph()
    title_par_2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title_2 = title_par_2.add_run(f"Consultation: {consultation_title}")
    set_heading_run_font(
        run_title_2, font_size=20, font_name="Calibri Light", is_bold=False
    )

    current_month_year = datetime.now().strftime("%B %Y")
    date_par = doc.add_paragraph()
    date_par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_date = date_par.add_run(current_month_year)
    set_run_font(run_date, font_size=14, font_name="Calibri")

    doc.add_page_break()

    exec_summary_heading = doc.add_heading("Executive Summary", level=1)
    exec_summary_heading.style = doc.styles["Heading 1"]
    set_run_font(
        exec_summary_heading.runs[0],
        font_name="Calibri Light",
        font_size=14,
        is_bold=True,
    )

    exec_summary_par = doc.add_paragraph()
    exec_summary_run = exec_summary_par.add_run(
        executive_summary_data.get("executive_summary", "")
    )
    set_run_font(exec_summary_run, font_size=10, font_name="Calibri")

    next_section = doc.sections[-1]
    next_section.left_margin = Inches(1)
    next_section.right_margin = Inches(1)
    next_section.top_margin = Inches(1)
    next_section.bottom_margin = Inches(1)

    is_first_chapter = True
    for chap_id in sorted_chapters:
        first_item = chapters_map[chap_id][0]
        chapter_title = first_item["chapter_title"].replace("#", "").strip()

        chapter_heading = doc.add_heading(chapter_title, level=1)
        chapter_heading.style = doc.styles["Heading 1"]
        set_run_font(
            chapter_heading.runs[0],
            font_name="Calibri Light",
            font_size=14,
            is_bold=True,
        )

        if not is_first_chapter:
            chapter_heading.paragraph_format.page_break_before = True
        is_first_chapter = False

        for item in chapters_map[chap_id]:
            q_heading = doc.add_heading("", level=2)
            q_heading.style = doc.styles["Heading 2"]
            q_heading.paragraph_format.space_after = Pt(8)
            q_heading.paragraph_format.left_indent = Inches(0.1)
            q_heading.paragraph_format.right_indent = Inches(0.1)

            run_q = q_heading.add_run(item["question"])
            set_run_font(run_q, font_size=11, font_name="Calibri", is_bold=True)

            pPr = q_heading._p.get_or_add_pPr()

            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:color"), "auto")
            shd.set(qn("w:fill"), "F2F2F2")
            pPr.append(shd)

            pBdr = OxmlElement("w:pBdr")
            for side in ["top", "left", "bottom", "right"]:
                border_elm = OxmlElement(f"w:{side}")
                border_elm.set(qn("w:val"), "single")
                border_elm.set(qn("w:sz"), "6")
                border_elm.set(qn("w:space"), "6")
                border_elm.set(qn("w:color"), "808080")
                pBdr.append(border_elm)
            pPr.append(pBdr)

            summary_par = doc.add_paragraph()
            run_summ = summary_par.add_run(item["response_summary"])
            set_run_font(run_summ, font_size=10, font_name="Calibri")
            summary_par.paragraph_format.space_after = Pt(8)

    output_filename = os.path.join(output_dir, "Consultation_Summary_Report.docx")
    doc.save(output_filename)





def merge_consecutive_cells(
    worksheet, df: pd.DataFrame, column_name: str, col_index: int, cell_format
) -> None:
    """
    Merges consecutive cells in a given column if they contain the same value.

    Args:
        worksheet: An `xlsxwriter` worksheet object where the cells will be merged.
        df (pd.DataFrame): The DataFrame containing the data.
        column_name (str): The column name whose values need to be merged.
        col_index (int): The index of the column in the worksheet.
        cell_format: The cell format to apply to the merged cells.
    """
    start_xl_row = 1
    last_data_row = start_xl_row + len(df) - 1
    
    
    def merge_run_if_needed(_worksheet, rstart: int, rend: int, value: str) -> None:
        """
        Merges a range of consecutive cells in a column if needed, otherwise writes a single value.

        Args:
            _worksheet (sheet): The worksheet to merge.
            rstart (int): The starting row index of the merge.
            rend (int): The ending row index of the merge.
            value (str): The value to write in the merged cells.
        """
        if rend > rstart:
            _worksheet.merge_range(rstart, col_index, rend, col_index, value, cell_format)
        else:
            _worksheet.write(rstart, col_index, value, cell_format)

    if len(df) == 0:
        return

    run_value = df.iloc[0][column_name]
    run_start = start_xl_row

    for i in range(1, len(df)):
        current_value = df.iloc[i][column_name]
        current_xl_row = start_xl_row + i

        if current_value != run_value:
            merge_run_if_needed(worksheet, run_start, current_xl_row - 1, run_value)
            run_value = current_value
            run_start = current_xl_row

    merge_run_if_needed(run_start, last_data_row, run_value)


def main_excel(
    consult_quest_summary_json: str,
    consultation_quest_json: str,
    segmented_json_file: str,
    output_dir: str,
) -> None:
    """
    Generates an Excel file summarizing consultation responses.

    Args:
        consult_quest_summary_json (str): Path to the consultation question summaries JSON file.
        consultation_quest_json (str): Path to the consultation questions JSON file.
        segmented_json_file (str): Path to the segmented consultation chapters JSON file.
        output_dir (str): Directory path where the Excel file will be saved.

    Raises:
        ValueError: If 'consultation_questions' key is missing in the consultation questions JSON file.
    """
    summaries = load_json(consult_quest_summary_json)
    cdata = load_json(consultation_quest_json)

    if "consultation_questions" in cdata:
        consultation_questions = cdata["consultation_questions"]
    else:
        raise ValueError(
            "consultation_questions.json does not contain 'consultation_questions' key!"
        )

    chapters_data = load_json(segmented_json_file)

    question_to_chapter_map = {}
    for cq in consultation_questions:
        qid = cq["id"]
        ch_id = cq["chapter_id"]
        question_to_chapter_map[qid] = ch_id

    chapter_map = {}
    for ch in chapters_data:
        cid = ch["chapter_id"]
        cid_str = str(cid)
        ctitle = ch["chapter_title"]
        chapter_map[cid_str] = ctitle

    data = {
        "Chapter Title": [],
        "Consultation Question": [],
        "Respondent Name": [],
        "Respondent Feedback": [],
        "Level of Agreement": [],
    }

    for entry in summaries:
        question_id = entry["question_id"]
        summary_json = entry["summary"]
        consultation_question = summary_json["consultation_question"]

        ch_id_val = question_to_chapter_map.get(question_id, None)
        if ch_id_val is None:
            chapter_title = "Unknown Chapter"
        else:
            chapter_title = chapter_map.get(str(ch_id_val), "Unknown Chapter")

        for resp in summary_json["responses"]:
            data["Chapter Title"].append(chapter_title)
            data["Consultation Question"].append(consultation_question)
            data["Respondent Name"].append(resp["respondent_name"])
            data["Respondent Feedback"].append(resp["response_summary"])
            data["Level of Agreement"].append(resp.get("respondent_agreement", ""))

    df = pd.DataFrame(data)

    excel_file = os.path.join(output_dir, "Consultation_Responses_Details.xlsx")
    with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Responses", index=False)

        workbook = writer.book
        worksheet = writer.sheets["Responses"]

        worksheet.freeze_panes(1, 0)
        worksheet.autofilter(0, 0, df.shape[0], df.shape[1] - 1)

        data_cell_format = workbook.add_format(
            {"text_wrap": True, "valign": "top", "align": "left"}
        )

        worksheet.set_column(0, 0, 40, data_cell_format)
        worksheet.set_column(1, 1, 40, data_cell_format)
        worksheet.set_column(2, 2, 30, data_cell_format)
        worksheet.set_column(3, 3, 120, data_cell_format)
        worksheet.set_column(4, 4, 20, data_cell_format)

        header_format = workbook.add_format(
            {"bold": True, "align": "left", "valign": "vcenter"}
        )
        for col_num, heading in enumerate(df.columns):
            worksheet.write(0, col_num, heading, header_format)

        merged_cell_format = workbook.add_format(
            {"align": "left", "valign": "top", "text_wrap": True}
        )

        chapter_col_idx = df.columns.get_loc("Chapter Title")
        merge_consecutive_cells(
            worksheet, df, "Chapter Title", chapter_col_idx, merged_cell_format
        )

        question_col_idx = df.columns.get_loc("Consultation Question")
        merge_consecutive_cells(
            worksheet, df, "Consultation Question", question_col_idx, merged_cell_format
        )


def consolidating_the_results(
    consult_quest_summary_json: str,
    consult_paper_info_json: str,
    executive_summary_json: str,
    consultation_quest_json: str,
    segmented_json_file: str,
    output_dir: str,
) -> None:
    """
    Consolidates consultation results by generating Word and Excel reports.

    Args:
        consult_quest_summary_json (str): Path to consultation question summaries JSON file.
        consult_paper_info_json (str): Path to consultation paper information JSON file.
        executive_summary_json (str): Path to executive summary JSON file.
        consultation_quest_json (str): Path to consultation questions JSON file.
        segmented_json_file (str): Path to consultation paper segmented JSON file.
        output_dir (str): Directory where the generated reports will be saved.
    """
    main_word(
        consult_quest_summary_json,
        consult_paper_info_json,
        executive_summary_json,
        output_dir,
    )
    main_excel(
        consult_quest_summary_json,
        consultation_quest_json,
        segmented_json_file,
        output_dir,
    )
