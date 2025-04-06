import json
from agents import Runner, trace
from llm.llm_engine import Vector_Store_Agent


async def agent_for_file_uploading(meta_data_file_path: str, output_dir: str) -> None:
    """
    Handles the process of uploading files based on metadata and output directory paths.

    Args:
    meta_data_file_path (str): Path to the metadata file that contains details of the processed files.
    output_dir (str): The output directory where the processed files should be uploaded.

    """

    with trace("Step 2: Vector Store Upload"):
        result = await Runner.run(
            Vector_Store_Agent,
            [
                {
                    "role": "user",
                    "content": "Call the upload files tool",
                    "arguments": {
                        "Metadata_File_path": meta_data_file_path,
                        "output_dir": output_dir,
                    },
                }
            ],
        )

        if result.final_output is not None:
            print(json.dumps(result.final_output, indent=4, ensure_ascii=False))
