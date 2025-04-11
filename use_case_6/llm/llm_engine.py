import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_response_from_openai(
    prompt: str, model: str = "o3-mini"
) -> Dict[str, Any]:
    """
    Generates a response using OpenAI's chat model.

    Parameters:
    prompt (str): The input prompt for the AI model.
    model (str): The model to use (default: "o3-mini").

    Returns:
    Dict[str, Any]: The API response containing the model's output.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    return response


def get_compliance_score_from_openai(prompt: str, model: str = "gpt-4o") -> str:
    """
    Sends a prompt to the OpenAI model to get a compliance score (0–10) based on the assessment.

    Args:
        prompt (str): The requirement being evaluated.
        model (str):client model (default =gpt-4o)

    Returns:
        str: The raw model response (expected to be an integer string from 0 to 10).
    """

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1,
        logprobs=True,
        top_logprobs=3,
    )

    return response


def get_prompt_for_outsourcing_agreement(markdown_text: str) -> str:
    """
    Generates a structured prompt for segmenting an outsourcing agreement.

    Parameters:
    markdown_text (str): The outsourcing agreement text in Markdown format.

    Returns:
    str: A formatted prompt incorporating the provided Markdown text.
    """

    return f""" 
    # Role & task
    You are presented with text of an outsourcing agreement in Markdown. Your task is to identify the agreements main logical units, reflecting its core logical structure. 

    # Instructions
    1. Read the text in full.
    2. Develop an understanding of the logical structure of the agreement.
    3. Based on this understanding, identify the main logical units of the agreement. 
    4. On the basis of the identified units, identify the starting points of the units and the associated Markdown markers. 
    5. Create an ordered JSON array listing the starting points of the logical units including any Markdown markers, whereby each item is a string. 
    
    # Additional rules
    * Strictly focus on the body of the agreement - ignore any table of contents 
    * Strictly return the name of the unit and the associated Markdown markers as shown in the body of the text; never remove or simplify any Markdown markers

    # Example outputs - please tailor as required

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

    Outsourcing agreement text in Markdown: {markdown_text}
    """


def get_prompt_for_contract_summary(
    requirement_description: str, matches_text: str
) -> str:
    """
    Generates a detailed prompt asking the model to summarize relevant contract provisions.

    Args:
        requirement_description (str): The requirement the contract needs to fulfill.
        matches_text (str): Matched content extracted from the agreement.

    Returns:
        str: Prompt to be used with the language model.
    """
    return f"""
        # Role:
        You are a financial supervision analyst tasked with carrying out a compliance assessment of a licensed entity's outsourcing agreement vis-à-vis regulatory requirements for the content of outsourcing agreements.
        Your specific task is to prepare a detailed overview of the provisions in the entity's outsourcing agreement relevant to the specific requirement. 
        
        # Instructions:
        1. Review in detail the specific requirement for the content of the outsourcing agreement. 
        2. Review the provided content from the agreement. 
        3. Prepare an objective and neutral overview of the provisions contained in the contract pertaining to the specific requirement.  
        
        # Output
        
        Your output consists of a detailed summary in continuous prose of the relevant provisions (no bullets).
        
        # Additional guidance:
        * Strictly only rely on the content from the agreement for your overview. 
        * Be as specific and detail-oriented in your overview.
        * Adopt expert-level language in the formulation of your summary. Maintain and objective and neutral position, stating facts consistent with your role as supervisor. 
        * Strictly do not offer any recommendations on the basis of the findings. Focus exclusively on providing an overview of the provisions. 

        # Inputs
        
        Requirement Description:
        {requirement_description}

        Relevant contract text identified for this requirement:
        {matches_text}

        """


def get_prompt_for_compliance_assessment(
    requirement_description: str, contract_contents: str
) -> str:
    """
    Creates a prompt asking the model to perform a qualitative compliance assessment.

    Args:
        requirement_description (str): Regulatory requirement to assess.
        contract_contents (str): Summary of contract provisions.

    Returns:
        str: Prompt for generating the compliance assessment.
    """

    return f"""
        # Role:
        You are a financial supervision analyst tasked with carrying out a compliance assessment of a licensed entity's outsourcing agreement vis-à-vis regulatory requirements for the content of outsourcing agreements.
        Your specific task is qualitatively assess the level of compliance of the content with a specific requirements based on the contents of the agreement.
        To that end, you are provided with the description of the requirement and a subset of the relevant content from the agreement.  

        # Instructions:
        1. Review in detail the specific requirement for the content of the outsourcing agreement. 
        2. Review the provided content from the agreement. 
        3. Determine the level of compliance of the content with the specific requirement, taking into account (a) whether the contract covers the content requirement at all and (b) the level of completeness and specificity with which the contnet requirement is addressed. 
        4. Prepare a summary of your findings complete with justifications. The justifications - where possible - must reference the specific sections from the contract agreement. 
        
        # Output
        
        Your output consists of a succinct yet specific summary of findings (no more than 3 sentences).
        
        # Additional guidance:
        * Strictly only rely on the content from the agreement for your assessment. 
        * Adopt expert-level language in the formulation of your summary. Maintain and objective and neutral position, stating facts consistent with your role as supervisor. 
        * Strictly do not offer any recommendations on the basis of the findings. Focus exclusively on stating the finding and supporting justification.
        
        # Inputs
        
        Requirement Description:
        {requirement_description}

        Summary of Contract Contents:
        {contract_contents}
        
        
        """


def get_prompt_for_compliance_score(
    requirement_description: str, compliance_assessment: str
) -> str:
    """
    Creates a prompt to assign a numeric compliance score based on a qualitative assessment.

    Args:
        requirement_description (str): The compliance requirement.
        compliance_assessment (str): The qualitative assessment text.

    Returns:
        str: Prompt for scoring compliance from 0 to 10.
    """

    return f"""
        # Role:
        You are a financial supervision analyst tasked with carrying out a compliance assessment of a licensed entity's outsourcing agreement vis-à-vis regulatory requirements for the content of outsourcing agreements.
        Your specific task is to assign a compliance score in the range from 0-10 for compliance with a specific requirements based on the qualitative analysis of the level of compliance. 

        # Instructions:
        1. Review in detail the specific requirement for the content of the outsourcing agreement. 
        2. Review the associated assessment of compliance and supporting justification based on the agreement's contents. 
        3. Based on the compliance assessment result, assign a quantitative score (integer) between 0 and 10 that adequately reflects the level of compliance whereby 10 indicates the highest level of compliance.
        
        # Output:
        
        Your output consists exclusively of a single integer for the score. You do not add any justification or other remarks. 
        
        # Additional guidance:
        * Strictly only rely on compliance assessment in the determination of the score. 
        * Refrain from adding any justification for your conclusion. 
        
        # Inputs
        
        Requirement:
        {requirement_description}

        Compliance assessment:
        {compliance_assessment}

        """
