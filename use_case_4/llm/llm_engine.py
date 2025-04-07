import json
import os
import logging
from typing import Optional, Tuple,Union
from openai import OpenAI,OpenAIError
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_prompt_to_generate_consultation_summary(markdown_text: str) -> str:
    """
    Generates a structured prompt for extracting and summarizing key information.

    Args:
        markdown_text (str): The full text of the consultation paper in markdown format.

    Returns:
        str: A formatted prompt.
    """
    return f"""
    # Role & task

    You are a financial regulatory policy specialist. You are provided with the text of a consultation paper. Your task is to extract and summarize all essential information from the consultation paper in a manner that produces a complete, stand-alone overview in the specified JSON format. Follow the structure and its bullets as closely as possible, matching the illustrative example’s style.

    General information
    * Title of Consultation Paper: Provide the exact document title and reference number (if applicable).  
    * Issuer / Authority: Identify the regulatory or supervisory authority proposing the consultation.  
    * Date of Publication: Provide the date the consultation paper was published.  
    * Consultation Deadline: Indicate the final date by which stakeholders should submit comments.  

    Purpose & rationale
    * Reason for Consultation: Summarize why the document is being issued (e.g., new regulatory requirements, clarifications of existing rules, industry developments).  
    * Policy Goals: Highlight what the authority aims to achieve (e.g., financial stability, consumer protection, market integrity, introduction of new frameworks).  

    Scope
    * Scope of Application: Specify which financial products, services, or market participants are covered (e.g., banks, payment service providers, virtual asset service providers, investment firms).  
    * Target Stakeholders (If Mentioned): Note particular audiences the consultation addresses (e.g., issuers, competent authorities, investors, consumer bodies).  

    Key definitions & concepts
    * Definitions: List important or newly introduced terms (e.g., “Fiat-Referenced Token,” “issuer-sponsored research”) as provided in the paper.  
    * Conceptual Clarifications: Summarize major new or revised concepts introduced in the paper.  

    Proposed measures & recommendations
    * Proposals / Recommendations: Describe what is being proposed or amended (new frameworks, rules, obligations, or definitions).  
    * Implementation Details: If stated, mention specific steps or schedules for implementation (e.g., new chapters in rulebooks, transitional periods).  

    ## Instructions

    1. Conduct an initial read-through  
    * Read the entire consultation paper once to understand its structure, main purpose, and style.  
    * Mark relevant sections or headings that map to each of the categories (Document Overview, Purpose & Rationale, Scope, etc.).

    2. Identify key segments  
    * Highlight text that pertains to each of the nine sections.  
    * Include stakeholder groups, proposed rule text, definitions, and consultation questions wherever mentioned.

    3. Identify the key information for each section
    * Document Overview: Extract title, date of publication, etc.  
    * Purpose & Rationale: Summarize the stated objectives or drivers.  
    * Scope: Note covered activities, products, or entities, plus target stakeholders if specified.  
    * Key Definitions & Concepts: Record new or revised terminology.  
    * Proposals / Recommendations: Extract the core proposals / recommendations  
    * Implementation details: Summarize information regarding implementation guidance, timelines etc.  

    4. Ensure Mutual Exclusivity and Standalone Clarity  
    * Each section should be understandable on its own, without requiring reference to other sections.  
    * Avoid duplicating the same information across sections.

    5. Ensure factual accuracy  
    * Accurately reflect information from the consultation paper; if details are unclear, note them as “ambiguous” or “not specified.”
    * Strictly only rely on the information presented in the consultation paper.
    * Do not add own opinions or personal recommendations.  

    6. Maintain consistency of terminology  
    * Use the terms exactly as they appear in the consultation.  
    * If paraphrasing for clarity, maintain consistent usage throughout your summary.

    # Output
    * Return your analysis in the form of a JSON as illustrated in the example
    * Use bulleted or numbered lists (as in the example) for clarity.  
    * Label each section clearly so the final result can stand alone without additional guidance.

    # Consultation Paper
    {markdown_text}
    """


def get_prompt_chapter_extraction_prompt(markdown_text:str) -> str:
    return f"""
    # Role & Task
    You are presented with text of a consultation paper in Markdown. Your task is to identify the text's main chapters, reflecting the consultation paper's core logical structure. 

    # Instructions
    1. Read the text in full.
    2. Identify the main chapters and the associated Markdown markers.
    3. Focus on top-level chapters only and refrain from including any detailed sub-sections.
    4. Create an ordered JSON array listing chapters with their respective Markdown titles, whereby each item is a string.

    # Example Outputs

    ## Example 1
    
    [
      "## Chapter 1 title",
      "## Chapter 2 title",
      "## Chapter 3 title",
      "## Chapter 4 title",
      "## Chapter 5 title"
    ]
    
    ## Example 2
    
    [
      "**Chapter 1 title**",
      "**Chapter 2 title**",
      "**Chapter 3 title**",
      "**Chapter 4 title**",
      "**Chapter 5 title**"
    ]

    # Input

    Text in Markdown:
    {markdown_text}
    """


def get_prompt_to_extract_questions(chapter_title: str, chapter_content: str) -> str:
    return f"""
    # Role & task
    You are given a text from a chapter of a consultation paper, comprising of a chapter title and the chapter content.
    Your task is to identify the consultation questions (if any) present in this chapter.

    # Instructions
    1. Read through the chapter content. 
    2. Identify any consultation question(s). A "consultation question" is typically a direct question the consultation paper is asking stakeholders to address.  
    3. Return the identified consultation question(s) or groups of questions as list in the form of a valid JSON. The questions must be returned verbatim. 
    4. Where multiple questions are logically grouped in the consultation paper, such as under a heading, label or number, you must strictly retain this grouping and treat them as a single question for the purpose of creating the list, i.e. you must combine them as a single list entry.
    4. If there are no consultation questions in this chapter, return an empty list.

    # Output
    Your response consists of a valid JSON object of the following format:

    {{
      "questions": [
        "Question 1 ... ?",
        "Question 2 ... ?",
        "Question 3a... ? Question 3b ...?"
        ...
      ]
    }}

    If no questions are identified, you return:
    
    {{
      "questions": []
    }}
    
    # Input
    
    Chapter title: {chapter_title}
    Chapter content: {chapter_content}
    """


def get_prompt_to_assign_chapter_ids(chapters_data: dict, questions_data: dict) -> str:
    """
    Generates a structured prompt for assigning chapter IDs to consultation questions.

    Args:
        chapters_data (dict): JSON object containing chapters with 'chapter_id', 'chapter_title', and 'chapter_content'.
        questions_data (dict): JSON object containing consultation questions.

    Returns:
        str: A formatted prompt for the LLM.
    """
    return f"""
    # Role & task
    You are given two JSON objects:
    
    1) 'chapters' from a consultation paper, each with an associated 'chapter_id', 'chapter_title', and 'chapter_content'.
    2) 'consultation_questions', which is a list of questions extracted from the entire paper.
    
    For each question in 'consultation_questions', your task is to identify the single most relevant 'chapter_id' from 'chapters'.
    This means figuring out which chapter the question likely belongs to. If uncertain, choose the best match.
    
    # Instructions
    1. Analyze each question and match it to exactly one chapter.
    2. Return the updated 'consultation_questions' as valid JSON with an additional 'chapter_id' key for every question.
       Each item in 'consultation_questions' should have: 'id', 'question', and 'chapter_id'.
    
    # Output
    Your response must be a valid JSON object of the form:
    {{
      "consultation_questions": [
        {{
          "id": "question_1",
          "question": "...",
          "chapter_id": "chapter_1"
        }}  
        ...
      ]
    }}
    
    # Input
    
    chapters: {json.dumps(chapters_data, ensure_ascii=False)}
    consultation_questions: {json.dumps(questions_data, ensure_ascii=False)}
    """


def get_prompt_to_identify_logical_units(markdown_text: str) -> str:
    """
    Generates a structured prompt to identify logical units within a Markdown-formatted consultation response.

    Args:
        markdown_text (str): The text of the consultation response in Markdown format.

    Returns:
        str: A formatted prompt instructing the AI to identify logical units in the text.
    """
    return f"""
    # Role & task
    You are presented with text of a response to a consultation paper in Markdown. Your task is to identify the text's main logical units, reflecting its core logical structure. 
    
    # Instructions
    1. Read the text in full.
    2. Develop an understanding of the logical structure of the text (e.g., by themes, by questions).
    3. Based on this understanding, identify the main logical units of the text. 
    4. On the basis of the identified units, identify the starting points of the units and—if applicable—the associated Markdown markers. 
    5. Focus on top-level chapters only and refrain from including any detailed sub-sections. 
    6. Create an ordered JSON array listing the starting points of the logical units, including any Markdown markers, whereby each item is a string. 
    
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

    Text in Markdown: {markdown_text}
    """


def get_prompt_to_identify_respondent(markdown_text: str) -> str:
    """
    Generates a structured prompt to identify the respondent (organization) from a consultation response.

    Args:
        markdown_text (str): The text of the consultation response in Markdown format.

    Returns:
        str: A formatted prompt instructing the AI to extract the respondent's name.
    """
    return f"""
    # Role & task
    You are presented with the response to a consultation paper. Your task is to identify the name of the organization submitting the response. Your response strictly only consists of the name of the respondent.

    # Input
    
    Text in Markdown: {markdown_text}
    """


def get_prompt_for_relevance_check(
    questions_str: str, heading: str, content: str
) -> str:
    """
    Generates a prompt for checking the relevance of a response chunk to consultation questions.

    Args:
        questions_str (str): A formatted string containing consultation questions with their IDs.
        heading (str): The heading of the response chunk.
        content (str): The content of the response chunk.

    Returns:
        str: A structured prompt instructing a model to evaluate the relevance of the response chunk.
    """

    return f"""
    # Role & Task
    You are a financial regulatory policy analyst. As part of the analysis of responses to a consultation paper, 
    you are to determine the relevance of specific responses to a given question. 

    To that end, you are provided with a set of consultation questions, each with an ID and text, and a single response chunk.
    You must determine whether the chunk is relevant (1) or not relevant (0) for a given consultation question.

    # Output Format
    Your output must be a JSON in the following structure:
    {{
        "relevance": {{
            "question_1": 0 or 1,
            "question_2": 0 or 1,
            ...
        }}
    }}

    # Consultation Questions
    {questions_str}

    # Response Chunk
    **Heading:** {heading}
    
    **Content:** {content}
    """.strip()


def get_prompt_for_summarizing_responses(
    question_data: dict,
    background_info: dict,
    chapter_content: str,
    previous_summaries: str = "",
) -> str:
    """
    Generates a structured prompt for summarizing consultation question responses.

    Args:
        question_data (dict): The consultation question details and responses.
        background_info (dict): Background information about the consultation.
        chapter_content (str): The content of the associated consultation chapter.
        previous_summaries (str, optional): Summaries of previous questions for context.

    Returns:
        str: A formatted prompt for the AI model.
    """

    question_text = question_data["question"]
    responses = question_data.get("responses", [])

    return f"""
    
    # Role & task

    You are a financial regulatory policy analyst. You are tasked with preparing a summary of responses to a recently issued consultation paper for further internal review and discussion. To that end, you are provided with several inputs:

    1. Responses to specific question(s) from the consultation paper.
    2. The original text from the chapter associated with the consultation questions.
    3. Background information about the consultation.
    4. Summaries of previous consultation questions (if any).

    # Instructions

    1. Fully read the text from the relevant chapter to understand the context and purpose of the consultation question(s).
    2. Examine each response, noting key points, agreements, disagreements, and any new insights or suggestions.
    3. Synthesize information into an integrated view, combining similar points or themes from different responses, identifying patterns. Additionally, include any notable suggestions or concerns with a potential impact on the further policy position. 
    4. Prepare a concise yet specific paragraph in expert-level language. Maintain technical terms consistent with those in the consultation paper and responses. 

    # Input
    ## Background information about the consultation:
    {json.dumps(background_info, ensure_ascii=False)}

    ## Summaries of previous questions:
    {previous_summaries}

    ## Consultation question and associated responses:
    {json.dumps({"question": question_text, "responses": responses}, ensure_ascii=False)}

    ## Chapter content of the consultation paper chapter associated with the question:
    {chapter_content}
    """


def get_prompt_for_executive_summary(
    background_info: dict, question_summaries: list
) -> str:
    """
    Generates a structured prompt for creating an executive summary of consultation responses.

    Args:
        background_info (dict): Background information about the consultation.
        question_summaries (list): Summaries of individual consultation questions.

    Returns:
        str: A formatted prompt for the AI model.
    """

    return f"""
    
    # Role & task

    You are a financial regulatory policy analyst. You are tasked with creating an overall executive summary providing insights on the responses to a consultation paper. 

    # Instructions

    1. Review the background information about the consultation paper.
    2. Analyze the summarized responses to the consultation questions, noting any major themes or recurring points.
    3. Synthesize the background information and analysis of the responses into a single, cohesive executive summary, clearly outlining any major themes from the consultation paper responses. 
    4. Discuss any potential policy implications derived from the identified themes and other relevant key takeaways. 

    # Output 
    * Two comprehensive paragraphs in expert-level language.
    * Maintain the same technical terms as used in the consultation paper and the responses.
    * Use clear, easy-to-follow sentence structures.
    * Do not add personal opinions or recommendations—strictly base the summary on the information provided.

    # Input
    ## Background information about the consultation:
    {json.dumps(background_info, ensure_ascii=False)}

    ## Summaries of individual consultation questions:
    {json.dumps(question_summaries, ensure_ascii=False, indent=2)}
    """


def fetch_openai_response(prompt: str) -> dict:
    """Helper function to get a JSON response from OpenAI"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content.strip())
    except json.JSONDecodeError as e:
        print("JSON decode error:", e)
        return {}
    except Exception as e:
        print("Error fetching response from OpenAI:", e)
        return {}


def openai_chat_request(
    prompt: str, model: Optional[str] = "o3-mini"
) -> Union[dict, list, str]:
    """
    Generic function to send a chat request to OpenAI and handle responses.
    Args:
        prompt (str): The input prompt for OpenAI.
        model (Optional[str]): The model name (default: "o3-mini").

    Returns:
        Union[dict, list, str]: Parsed JSON response, list, or raw response string.
    """
    try:
        response = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}]
        )

        response_content = response.choices[0].message.content.strip()

        try:
            return json.loads(response_content)
        except json.JSONDecodeError:
            return response_content

    except Exception as e:
        return {"error": str(e)}


def get_response_from_openai(prompt: str, model: str = "gpt-4o-mini") -> Tuple[Optional[str], Optional[str]]:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )

        if not response.choices or not hasattr(response.choices[0], "message"):
            raise ValueError("Unexpected response format from the model.")

        return response.choices[0].message.content.strip(), None

    except (OpenAIError, ValueError, Exception) as e:
        logging.exception(f"Error from OpenAI: {e}")
        return None, str(e)