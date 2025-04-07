import json
import os
from typing import List, Dict
from agents import Runner, trace
from utils.file_handler import read_json_file, write_to_json_file
from llm.llm_engine import Chunk_Mapping_Agent, Outline, ContentChunk, MappingOutput


async def agent_for_content_outline_mapping(output_dir: str) -> None:
    """
    This function processes the outline and search results to map content chunks to an outline.

    Args:
    - output_dir (str): The directory where the output files (e.g., outline.json, search_results.json) are located.

    """
    outline_file = os.path.join(output_dir, "outline.json")
    outline_data = read_json_file(outline_file)
    outline = Outline(**outline_data)

    search_results_file = os.path.join(output_dir, "search_results.json")

    search_data = read_json_file(search_results_file)
    consolidated = search_data.get("consolidated_results", [])

    file_chunk_map: Dict[str, List[ContentChunk]] = {}

    for entry in consolidated:
        file_name = entry.get("file_name")
        chunks_raw = entry.get("filtered_search_results", [])

        for chunk in chunks_raw:
            chunk_id = chunk.get("ID")
            content_list = chunk.get("content", [])
            content_str = "\n".join(content_list).strip()
            if not chunk_id or not content_str:
                continue
            file_chunk_map.setdefault(file_name, []).append(
                ContentChunk(ID=chunk_id, content=content_str, file_name=file_name)
            )

    with trace("Step 5: Content Mapping"):
        for file_name, chunks in file_chunk_map.items():
            print(f">>> Mapping chunks from file: {file_name}")

            mapping_input = {
                "role": "user",
                "content": json.dumps(
                    {
                        "outline": outline.model_dump(),
                        "file_chunks": [chunk.model_dump() for chunk in chunks],
                    },
                    indent=2,
                ),
            }

            result = await Runner.run(Chunk_Mapping_Agent, input=[mapping_input])
            mapped_output: MappingOutput = result.final_output_as(MappingOutput)
            outline = mapped_output.updated_outline
    outline_mapped_file = os.path.join(output_dir, "outline_mapped.json")

    write_to_json_file(outline_mapped_file, outline.model_dump(), indent=4)

    id_to_content = {}
    for result in search_data.get("consolidated_results", []):
        for search_result in result.get("filtered_search_results", []):
            id_ = search_result["ID"]
            id_to_content[id_] = {
                "organization": search_result.get("organization"),
                "title": search_result.get("title"),
                "year": search_result.get("year"),
                "content": "\n".join(search_result.get("content", [])),
            }

    enriched_outline = outline.model_dump()

    for chapter in enriched_outline.get("chapters", []):
        mapped_ids = chapter.pop("mapped_ids", [])
        chapter["mapped_content"] = []
        for mapped_id in mapped_ids:
            if mapped_id in id_to_content:
                chapter["mapped_content"].append(id_to_content[mapped_id])
    outline_mapped_content_file = os.path.join(
        output_dir, "outline_mapped_content.json"
    )
    write_to_json_file(outline_mapped_content_file, enriched_outline, indent=4)
