from agents import Agent, ModelSettings, Runner, trace
from retrieval.retriever import search_file


async def performing_sematic__file_search(output_dir: str) -> None:
    """
    Performs a semantic file search using the File Search Agent and the search_file tool.

    Args:
    output_dir (str): Path to the directory where the files to be searched are stored.

    Returns:
     None
    """
    file_search_agent = Agent(
        model="gpt-4o-mini",
        name="File Search Agent",
        tools=[search_file],
        model_settings=ModelSettings(tool_choice="required"),
        tool_use_behavior="stop_on_first_tool",
    )

    with trace("Step 3: File Search"):
        await Runner.run(
            file_search_agent,
            [
                {
                    "role": "user",
                    "content": "Call the search file tool",
                    "arguments": {"output_dir": output_dir},
                }
            ],
        )
