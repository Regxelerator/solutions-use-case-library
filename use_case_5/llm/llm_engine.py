from openai import OpenAI
from dotenv import load_dotenv
import os
import json


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_prompt_for_regulation_overview(markdown_text: str) -> str:
    """
    Generates a prompt to extract an overview of a regulation.

    Parameters:
        markdown_text (str): The regulation text in Markdown format.

    Returns:
        str: A formatted prompt string to be used in an AI model request.
    """
    return f"""
    # Role & task
    You are presented with the text from a regulation. Your task is to prepare an overview of the regulation. The overview should cover the following aspects:

    * Country of the authority that has issued the regulation
    * Name of the authority
    * Title of the regulation
    * Purpose of regulation
    * Scope of provisions covered under the regulation

    # Output

    Your output consists of a valid JSON of the following structure: 

    {{
    "regulation_overview": [
        {{
        "country": "[Country of the issuing authority]",
        "authority": "[Full name of the issuing authority including the country identifier]",
        "title": "[Title of the regulation]",
        "purpose": "[Purpose of the regulation]",
        "scope": "[Scope of provisions covered under the regulation]"
        }}
    ]
    }}

    # Input

    Text in Markdown: {markdown_text}
    """


def get_prompt_to_identify_logical_units(markdown_text: str) -> str:
    """
    Generates a prompt to identify the main logical units of a regulation.

    Parameters:
        markdown_text (str): The regulation text in Markdown format.

    Returns:
        str: A formatted prompt string to be used in an AI model request.
    """
    return f"""
    # Role & task
    You are presented with text of a regulation in Markdown. Your task is to identify the regulations' main logical units, reflecting its core logical structure. 

    # Instructions
    1. Read the text in full.
    2. Develop an understanding of the logical structure of the regulation.
    3. Based on this understanding, identify the main logical units of the text at the most granular level. 
    4. On the basis of the identified units, identify the starting points of the units and - if applicable - the associated Markdown markers. 
    6. Create an ordered JSON array listing the starting points of the logical units including any Markdown markers, whereby each item is a string. 

    # Example outputs

    ## Example 1

    [
    "## Title logical unit 1",
    "## Title logical unit 2",
    "## Title logical unit 3",
    "## Title logical unit 4",
    "## Title logical unit 5"
    ]

    ## Example 2

    [
    "**Title logical unit 1**",
    "**Title logical unit 2**",
    "**Title logical unit 3**",
    "**Title logical unit 4**",
    "**Title logical unit 5**"
    ]
    
    # Input

    Regulatory text in Markdown: {markdown_text}
    """


def get_prompt_for_logical_unit_summary(logical_unit_content: str) -> str:
    """
    Generates a prompt to summarize a logical unit from a financial regulation.

    Parameters:
        logical_unit_content (str): The text content of a specific logical unit.

    Returns:
        str: A formatted prompt string to be used in an AI model request.
    """
    return f"""
    You are presented with a section from a financial regulation. 
    Your task is to succinctly summarize the nature of provisions covered, without detailing the provisions themselves.
    The summary must be written such that it can be understood by a third party without additional context. 
    If the content of the section is not substantial or there is no content at all, you reply with 'Not applicable'. 

    {logical_unit_content}
    """


def get_prompt_for_benchmarking_dimensions(combined_input: str) -> str:
    """
    Generates a prompt for extracting benchmarking dimensions from regulatory outlines.

    Args:
        combined_input (str): The combined outline of regulations subject to benchmarking.

    Returns:
        str: A formatted prompt string for OpenAI's API.
    """
    return f"""
    # Role & task
    You are a financial regulatory policy analyst tasked with performing a comparative analysis of regulations from different jurisdictions. 
    You have been provided with an outline of the main contents of several regulations subject to analysis. 
    As a starting point for your work, you are to prepare an analysis framework, defining the benchmarking dimensions based on the content of the regulations.

    # Instructions
    1. Review the outlines of the main contents of the provided regulations.
    2. Identify key themes, topics, and elements within the regulations that are suitable for benchmarking.
    3. Define distinct benchmarking dimensions to enable a structured and comparative analysis across jurisdictions.
    4. In addition to the label for the benchmarking dimension, prepare a description detailing the scope of the dimension. 

    # Output
    Your output consists of a valid JSON defining the benchmarking dimensions, strictly following the following schema:

    {{
    "benchmarking_dimensions": [
        {{
        "dimension_1": "[Dimension label: Description of the scope of the dimension]",
        "dimension_2": "[Dimension label: Description of the scope of the dimension]"
        }}
    ]
    }}

    # Additional guidance
    * The dimensions must be sufficiently specific to allow for a detailed analysis of the provisions.
    * The identified benchmarking dimensions must be collectively exhaustive and cover all aspects addressed in the regulations.
    * A benchmarking dimension should be included in the analysis framework, even if it is only covered in a subset of the regulations.
    * The benchmarking dimension description should be in the form of a single comprehensive sentence, written in expert-level language and using the same technical terms as in the source regulations.
    * The description must be written such that it can be understood by a third party without additional context.
    * The selection of benchmarking dimensions and their descriptions should only be derived from the content provided. Do not add any additional dimensions that are not reflected in the regulatory texts.

    # Input
    Outline of regulations subject to benchmarking:
    {combined_input}
    """


def get_prompt_for_mapping_logical_units(
    dimension_text: str, lu_id: int, lu_heading: str, lu_summary: str
) -> str:
    """
    Generates a prompt for mapping a logical unit from a regulatory text to predefined benchmarking dimensions.
    Args:
        dimension_text (str): The full list of benchmarking dimensions, including labels and descriptions.
        lu_id (int): The unique identifier for the logical unit.
        lu_heading (str): The heading/title of the logical unit.
        lu_summary (str): A summary of the logical unit.

    Returns:
        str: A formatted prompt string for OpenAI's API.
    """
    return f"""
            # Role & task
            You are a financial regulatory policy analyst. 
            As a basis for a regulatory benchmarking exercise, you are tasked with mapping the content 
            (logical units) from a regulatory text to defined benchmarking dimensions.

            # Instructions
            1. Read through the content of the logical unit. 
            2. Read through the descriptions of the benchmarking dimensions. 
            3. Determine for which benchmarking dimensions the logical unit has relevance based on the description of the benchmarking dimension. 
            4. For each benchmarking dimension, indicate whether the logical unit has relevance [1] or has no relevance [0].

            # Additional guidance
            * A logical unit also has relevance if only a subset of its content pertains to the benchmarking dimension.
            * A logical unit can be mapped to multiple benchmarking dimensions.  

            # Input
            Here is the full list of benchmarking dimensions (label + scope/description):
            {dimension_text}

            Single logical unit to evaluate:
            Logical Unit ID: {lu_id}
            Heading: {lu_heading}
            Summary: {lu_summary}

            # Output
            The output must be valid JSON with the following structure (please keep the double brackets):
            {{
              "benchmarking_dimensions_mapping": [
                {{
                  "dimension_1": 0 or 1,
                  "dimension_2": 0 or 1,
                  ...
                }}
              ]
            }}
            """.strip()


def get_prompt_for_unmapped_logical_unit(
    dimension_overview_text: str,
    regulation_tag: str,
    lu_id: int,
    lu_heading: str,
    lu_summary: str,
) -> str:
    """
    Generates a prompt for mapping an unmapped logical unit from a regulatory text to benchmarking dimensions.

    Args:
        dimension_overview_text (str): Overview of existing benchmarking dimensions.
        regulation_tag (str): The identifier or tag for the regulation.
        lu_id (int): The unique identifier for the logical unit.
        lu_heading (str): The heading/title of the logical unit.
        lu_summary (str): A summary of the logical unit.

    Returns:
        str: A formatted prompt string for OpenAI's API.
    """
    return f"""
        # Role & task
        You are a financial regulatory policy analyst, responsible for undertaking a regulatory benchmarking. 
        As part of the preparatory work, you must map content (logical units) from regulations subject to analysis to defined benchmarking dimensions. 
        Part of the mapping has already been completed. You are now provided with a logical unit, which is currently unmapped. 
        Your task is to map this remaining logical unit. 
        
        You can accomplish this by either:
        (1) Adding the unmapped logical unit to existing benchmarking dimensions 
        (2) Creating one or multiple additional benchmarking dimensions to which this logical unit can be mapped (dimension_N+1, dimension_N+2, etc.)

        # Output
        Your output consists of the list of benchmarking dimensions (one or multiple) that the unit maps to, complete with their label and description. 
        If a new benchmarking dimension is created, then you must define a new label and description in line with the existing dimensions. 
        If in doubt about the dimension label, you can label it 'Others'. 
        In the JSON, strictly only list the dimension(s) to which the unmapped logical unit should be mapped.

        {{
            "benchmarking_dimensions_mapping": [
            {{
                "dimension_XX": "Benchmarking dimension label: benchmarking dimension description",
                "dimension_YY": "Another dimension label: dimension description",
                ...
            }}
            ]
        }}
        
        # Input
        
        # Existing dimension overview
        {dimension_overview_text}

        # Unmapped Logical Unit
        Regulation: {regulation_tag}
        Logical Unit ID: {lu_id}
        Heading: {lu_heading}
        Summary: {lu_summary}
        """.strip()


def get_prompt_for_non_core_dimensions(mapped_dimensions: dict) -> str:
    """
    Generates a structured prompt for identifying non-core benchmarking dimensions.

    Args:
        mapped_dimensions (dict): The JSON containing benchmarking dimensions
                                  and their mapped regulatory content.

    Returns:
        str: A formatted prompt for an AI model to analyze and identify
             non-core dimensions.
    """
    return f"""
    # Role & task
    You are a financial regulatory policy analyst responsible for performing a benchmarking/comparative analysis of regulations from multiple jurisdictions.
    You are provided with a JSON that includes a breakdown of the benchmarking dimensions complete with the content from the regulations subject to analysis. 
    Your task is to single out benchmarking dimensions that are not relevant to the core of the analysis of the topic, e.g., as a result of the content of the associated logical units being generic or immaterial.
    A dimension is still relevant even if it only contains content from one of the regulations. 
    It is solely the nature of the content of the dimensions and the associated logical units that should determine whether it is relevant or not. 

    # Output
    Your output consists of a JSON of the following structure:
    {{
        "non_core_dimensions": ["dimension_key_1", "dimension_key_2", ...]
    }}

    If all dimensions are relevant, return an empty array for 'non_core_dimensions'.

    # Input

    {json.dumps(mapped_dimensions, indent=2)}
    """


def get_prompt_to_prepare_comparative_analysis(
    dimension_description: str, benchmarking_framework: str, combined_overviews: str
) -> str:
    """
    Generates a structured prompt for conducting a comparative benchmarking analysis
    of financial regulations across multiple jurisdictions.

    Args:
        dimension_description (str): A description of the benchmarking dimension
        benchmarking_framework (str): The framework outlining the structure and
                                      methodology of the benchmarking analysis.
        combined_overviews (str): A summarized overview of country-specific
                                  regulations relevant to the analysis.

    Returns:
        str: A formatted prompt instructing an AI model to perform a comparative
             analysis of financial regulatory provisions.
    """

    return f"""
    # Role & Task
    You are a financial regulatory policy analyst responsible for performing a benchmarking/comparative analysis of regulations from multiple jurisdictions.
    For the purpose of the benchmarking, an analysis framework was created that breaks down the analysis into multiple dimensions. For each dimension, content from the regulations has been mapped.
    Your task is now to prepare the comparative analysis for a given dimension as follows. For that purpose, you are provided with the name and description of the analysis dimension and the associated regulatory clauses from the country-specific regulations.

    # Instructions
    1. Read through the dimension description and form an understanding of the scope of the benchmarking dimension.
    2. Read through the mapped regulatory clauses from each country-specific regulation.
    3. For each country, articulate the specific provisions through the lens of the analysis dimension. In doing so, you should follow a consistent logic.
    4. Additionally, synthesize the main commonalities and differences in the provisions.

    # Output
    Your output consists of a valid JSON. The JSON must strictly follow this structure (note: always keep the key provisions_country_1 etc. generic).

    {{
        "benchmarking_analysis": 
            {{
                "country_provisions": {{
                    "provisions_country_1": "[Overview of the specific provisions for country 1]",
                    "provisions_country_2": "[Overview of the specific provisions for country 2]",
                    "..."
                }},
                "comparative_analysis": "[Synthesis of the main commonalities and differences]"
            }}
    }}

    # Additional Guidance
    * Ensure your analysis adheres strictly to the scope of the dimension, ignoring any provisions outside the dimension's focus.
    * Keep your analysis precise and specific, using expert-level language while acknowledging technical terms as per the regulations.
    * Strictly anchor your analysis in the provided provisions.
    * If there are no provisions for a given benchmarking dimension and country, then strictly return "This dimension is not covered in the country's regulation."
    * Maintain objectivity and neutrality without adding personal opinions or recommendations.

    # Input

    **Benchmarking Analysis Framework:** 
    {benchmarking_framework}

    **Overview of Country-Specific Regulations:** 
    {combined_overviews}

    **Dimension Description with Mapped Country-Specific Provisions:** 
    {dimension_description}
    """


def get_openai_response(
    prompt: str,
    model: str = "gpt-4o",
) -> str:
    """
    Sends a prompt to OpenAI's API and retrieves the response.

    This method is fully generic and includes error handling to ensure smooth operation
    even in the case of API errors or unexpected responses.

    Args:
        prompt (str): The input prompt for the AI model.
        model (str, optional): The OpenAI model to use (default: "gpt-4o").
    Returns:
        str: The AI-generated response, or an error message if the request fails.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        if response.choices:
            return response.choices[0].message.content.strip()
        else:
            raise ValueError("Received empty response from OpenAI API.")

    except Exception as e:
        error_message = f"Error occurred while fetching OpenAI response: {str(e)}"
        print(error_message)
        return error_message



def get_openai_response2(
    prompt: str,
    model: str = "gpt-4o",
    response_format: dict = None,
) -> str:
    """
    Sends a prompt to OpenAI's API and retrieves the response.

    This method is fully generic and includes error handling to ensure smooth operation
    even in the case of API errors or unexpected responses.

    Args:
        prompt (str): The input prompt for the AI model.
        model (str, optional): The OpenAI model to use (default: "gpt-4o").
        temperature (float, optional): Sampling temperature for response generation (default: 0.1).
        response_format (dict, optional): The response format specification (default: None).

    Returns:
        str: The AI-generated response, or an error message if the request fails.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format=response_format,
        )
        if response.choices:
            return response.choices[0].message.content.strip()
        else:
            raise ValueError("Received empty response from OpenAI API.")

    except Exception as e:
        error_message = f"Error occurred while fetching OpenAI response: {str(e)}"
        print(error_message)
        return error_message