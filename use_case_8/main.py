import os
import asyncio
from scripts.agent_1_file_processing_ import agent_for_file_processing
from scripts.agent_2_file_upload import agent_for_file_uploading
from scripts.agent_3_file_search import performing_sematic__file_search
from scripts.agent_4_outline_formulation import outlining_formulation
from scripts.agent_5_content_outline_mapping import agent_for_content_outline_mapping
from scripts.agent_6_report_writing import agent_for_report_writing
from scripts.agent_7_report_finalization import agent_for_report_finalization


async def main():
    """
    When this file is executed, the code will run in the following sequence:

    1. agent_1_file_processing_.py
    2. agent_2_file_upload.py
    3. agent_3_file_search.py
    4. agent_4_outline_formulation.py
    5. agent_5_content_outline_mapping.py
    6. agent_6_report_writing.py
    7. agent_7_report_finalization.py
    """

    input_dir = os.path.join(os.getcwd(), "input")
    if not os.path.exists(input_dir):
        raise FileNotFoundError(
            f"Input directory '{input_dir}' not found. Please ensure it exists and contains the required files."
        )
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)
    print("(--------Agent1 ------------)\n")
    metadata_path = await agent_for_file_processing(input_dir, output_dir)
    print("(--------Agent2------------)\n")
    await agent_for_file_uploading(metadata_path, output_dir)
    print("(--------Agent3 ------------)\n")
    await performing_sematic__file_search(output_dir)
    print("(--------Agent4 ------------)\n")
    await outlining_formulation(output_dir)
    print("(--------Agent5 ------------)\n")
    await agent_for_content_outline_mapping(output_dir)
    print("(--------Agent6 ------------)\n")
    await agent_for_report_writing(output_dir)
    print("(--------Agent7 ------------)\n")
    await agent_for_report_finalization(output_dir)
    print("(--------Completed ------------)\n")


if __name__ == "__main__":
    asyncio.run(main())