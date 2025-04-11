from agents import Runner, trace
from llm.llm_engine import file_search_agent


async def performing_sematic__file_search(output_dir: str) -> None:
    """
    Performs a semantic file search using the File Search Agent and the search_file tool.

    Args:
    output_dir (str): Path to the directory where the files to be searched are stored.

    Returns:
     None
    """

    with trace("Step 3: File Search"):
        await Runner.run(
            file_search_agent,
            [
                {
                    "role": "user",
                    "content": (
                        f"Search the files in the directory '{output_dir}' using the file search tool. "
                        "Return relevant matches or metadata."
                    ),
                }
            ],
        )
