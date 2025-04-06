import json
from agents import Runner, trace
from llm.llm_engine import Report_Agent


async def agent_for_report_finalization(output_dir: str) -> None:
    """
    Finalizes the report generation by calling the Report_Agent to create a Word document.

    Args:
        output_dir (str): The directory where the final report should be saved.

    Returns:
        None: The generated file is saved to output/Final Report/Final_Report.docx
    """

    with trace("Step 7: Report Generation"):
        result = await Runner.run(
            Report_Agent,
            [
                {
                    "role": "user",
                    "content": "Generate the final report in Word.",
                    "arguments": {"output_dir": output_dir},
                }
            ],
        )

        if result.final_output is not None:
            print(json.dumps(result.final_output, indent=4, ensure_ascii=False))
