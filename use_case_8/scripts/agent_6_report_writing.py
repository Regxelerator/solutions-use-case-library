import json
import os
from typing import List, Optional
from agents import Runner, ItemHelpers, TResponseInputItem, trace
from llm.llm_engine import (
    Report_Reviewer_Agent,
    Writer_Agent,
    Outline1 as Outline,
    ReportReviewerOutput,
)
from utils.file_handler import write_to_json_file, read_json_file


async def agent_for_report_writing(output_dir) -> None:
    """
    This function processes the outline and search results to map content chunks to an outline.

    Args:
    - output_dir (str): The directory where the final output files  will be located.

    """
    outline_file = os.path.join(output_dir, "outline.json")
    outline_data = read_json_file(outline_file)
    outline_mapped_file = os.path.join(output_dir, "outline_mapped_content.json")

    mapped_content_data = read_json_file(outline_mapped_file)
    outline = Outline(chapters=outline_data["chapters"])
    final_chapter_texts: List[Optional[str]] = [None] * len(outline.chapters)
    last_writer_output: str = ""
    reviewer_input: List[TResponseInputItem] = [
        {
            "role": "user",
            "content": (
                "Here is the report outline:"
                f"{json.dumps(outline_data, indent=2)}"
                "So far, no chapters are completed. Please coordinate chapter writing."
            ),
        }
    ]
    with trace("Step 6: Report Creation"):
        while True:
            completed_chapters = [
                i + 1 for i, text in enumerate(final_chapter_texts) if text
            ]
            if completed_chapters:
                msg = "Completed chapters so far:"
                for ch_num in completed_chapters:
                    ch_text = final_chapter_texts[ch_num - 1]
                    chapter_title = outline.chapters[ch_num - 1].get(
                        "title", f"Chapter {ch_num}"
                    )
                    msg += f"=== Chapter {ch_num}: {chapter_title} ==={ch_text}"
                reviewer_input.append({"role": "user", "content": msg.strip()})
            else:
                reviewer_input.append(
                    {"role": "user", "content": "No chapters completed so far."}
                )
            if last_writer_output:
                reviewer_input.append(
                    {
                        "role": "assistant",
                        "content": f"Here is the MOST RECENT chapter text (not yet final):{last_writer_output}",
                    }
                )
            print(">>> Calling reviewer agent to decide next step.")
            reviewer_result = await Runner.run(Report_Reviewer_Agent, reviewer_input)
            reviewer_output: ReportReviewerOutput = reviewer_result.final_output
            print(
                "Reviewer response => status:",
                reviewer_output.status,
                "next_writer_instruction:",
                reviewer_output.next_writer_instruction,
                "current_chapter:",
                reviewer_output.current_chapter,
            )
            if reviewer_output.status == "all_done":
                if (
                    reviewer_output.current_chapter is not None
                    and not final_chapter_texts[reviewer_output.current_chapter - 1]
                ):
                    final_chapter_texts[reviewer_output.current_chapter - 1] = (
                        last_writer_output
                    )
                    print(
                        f">>> Chapter {reviewer_output.current_chapter} accepted automatically on all_done."
                    )
                print(">>> Reviewer says all chapters are complete. Stopping.")
                break
            if (
                reviewer_output.status == "pass"
                and reviewer_output.current_chapter is not None
            ):
                chapter_idx = reviewer_output.current_chapter - 1
                final_chapter_texts[chapter_idx] = last_writer_output
                print(f">>> Chapter {reviewer_output.current_chapter} accepted.")
            instruction_for_writer = reviewer_output.next_writer_instruction
            print(">>> Calling writer agent with instruction:")
            print(instruction_for_writer)
            writer_input = []
            outline_msg = {
                "role": "system",
                "content": f"Outline:{json.dumps(outline_data, indent=2)}",
            }
            completed_msg = ""
            for i, text in enumerate(final_chapter_texts):
                if text:
                    t = outline.chapters[i].get("title", f"Chapter {i + 1}")
                    completed_msg += f"=== Chapter {i + 1}: {t} ==={text}"
            if completed_msg.strip():
                completed_msg = "Approved chapters so far:" + completed_msg.strip()
            chapters_msg = {
                "role": "user",
                "content": completed_msg or "No approved chapters yet.",
            }
            writer_input.append(outline_msg)
            writer_input.append(chapters_msg)
            writer_input.append({"role": "user", "content": instruction_for_writer})
            if (
                reviewer_output.current_chapter is not None
                and reviewer_output.current_chapter >= 1
                and reviewer_output.current_chapter <= len(outline.chapters)
            ):
                chapter_idx = reviewer_output.current_chapter - 1
                mapped_content_list = mapped_content_data["chapters"][chapter_idx].get(
                    "mapped_content", []
                )
                if mapped_content_list:
                    chunk_text = "Relevant content for this chapter:"
                    for c in mapped_content_list:
                        org = c.get("organization", "")
                        doc_title = c.get("title", "")
                        year = c.get("year", "")
                        cnt = c.get("content", "")
                        chunk_text += (
                            f"ORGANIZATION: {org}TITLE: {doc_title}YEAR: {year}{cnt}"
                        )
                    writer_input.append({"role": "user", "content": chunk_text})
            if reviewer_output.status == "needs_improvement":
                writer_input.append(
                    {"role": "assistant", "content": last_writer_output}
                )
            writer_result = await Runner.run(Writer_Agent, writer_input)
            last_writer_output = ItemHelpers.text_message_outputs(
                writer_result.new_items
            )
            print(">>> Writer produced the following draft:")
            print(last_writer_output)
    print("========= FINAL REPORT ========")
    final_chapters_json = []
    for idx, chapter_info in enumerate(outline.chapters):
        chapter_text = final_chapter_texts[idx] or "(No text provided.)"
        try:
            parsed_chapter = json.loads(chapter_text)
            final_chapters_json.append(parsed_chapter)
        except json.JSONDecodeError:
            fallback = {
                "response": {
                    "title": chapter_info.get("title", f"Chapter {idx + 1}"),
                    "subsections": [
                        {"title": "Error parsing chapter", "text": chapter_text}
                    ],
                }
            }
            final_chapters_json.append(fallback)
    final_report_path = os.path.join(output_dir, "final_report.json")
    final_report_dict = {"report": final_chapters_json}
    write_to_json_file(final_report_path, final_report_dict, indent=4)
    print(f">>> Final report saved to {final_report_path}")
