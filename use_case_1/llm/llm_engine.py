from openai import OpenAI
from dotenv import load_dotenv
import os
import time

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_category(complaint_text: str, model_name: str) -> str:
    """
    Classifies a consumer complaint using the fine-tuned model.

    Args:
        complaint_text (str): The complaint text to be classified.
        model_name (str): The fine-tuned model name.

    Returns:
        str: The predicted category label or 'Unknown' in case of failure.
    """
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": get_prompt_for_fine_tuned_classification(),
                },
                {"role": "user", "content": create_user_prompt(complaint_text)},
            ],
            temperature=0.0,
        )
        return completion.choices[0].message.content.strip()

    except Exception as e:
        print(
            f"[Error] Failed to classify complaint: {complaint_text[:60]}... -> {str(e)}"
        )
        return ""


def generate_gpt_response(
    prompt: str, user_message: str, model: str = "gpt-4o", temperature: float = 0.01
) -> str:
    """
    Generates a response from the GPT model based on the given prompt and user input.

    Args:
        prompt (str): The system message providing classification instructions and examples.
        user_message (str): The user input text to be classified.
        model (str, optional): The OpenAI GPT model to use. Defaults to "gpt-4o".
        temperature (float, optional): The temperature for response creativity. Defaults to 0.01.

    Returns:
        str: The model's response as a classification label or an error message.
    """
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"


def fine_tune_model(jsonl_filename: str) -> str:
    """
    Uploads the JSONL training file and initiates the fine-tuning process.

    Args:
        jsonl_filename (str): Path to the JSONL file.

    Returns:
        str: The ID of the fine-tuned model.
    """
    upload_response = client.files.create(
        file=open(jsonl_filename, "rb"), purpose="fine-tune"
    )
    file_id = upload_response.id

    finetune_response = client.fine_tuning.jobs.create(
        training_file=file_id, model="gpt-4o-2024-08-06"
    )
    job_id = finetune_response.id

    print("Fine-tuning in progress. This may take some time...")

    while True:
        retrieved_job = client.fine_tuning.jobs.retrieve(job_id)
        status = retrieved_job.status

        if status in ["succeeded", "failed", "cancelled"]:
            break

        time.sleep(600)

    if status == "succeeded":
        print("Fine-tuning completed successfully!")
        return retrieved_job.fine_tuned_model
    else:
        print(f"Fine-tuning failed or was cancelled. Status: {status}")
        return ""


def get_prompt_for_fine_tuned_classification() -> str:
    """
    Returns the system prompt for fine-tuned classification of consumer complaints.

    The prompt instructs the model to classify complaints into predefined categories.
    """
    return """
    # Role 
    You are a supervision analyst with a specialization in conduct and consumer protection. Your role is to classify individual consumer complaints by nature of issue. 

    # Instruction
    Read through the consumer complaint and classify it into one of the following categories: advertising, account closure, application denial, customer service, disclosure, fees, fraud and loan repayment. Your response strictly only consists of the category label. 
    """


def create_user_prompt(complaint_text: str) -> str:
    """
    Generates a user message format for classification.

    Args:
        complaint_text (str): The complaint text to be classified.

    Returns:
        str: Formatted complaint message.
    """
    return f"Complaint: {complaint_text}"


def get_prompt_for_few_short_classification() -> str:
    """
    Generates the system message prompt for classifying consumer complaints.

    Returns:
        str: A formatted system message containing classification categories, descriptions,
             instructions, and labeled complaint examples.
    """
    return """
    # Role & task
    You are a supervision analyst with a specialization in conduct and consumer protection. Your role is to classify individual consumer complaints by nature of issue. 

    # Instruction
    Read through the consumer complaint and classify it into one of the following categories: advertising, account closure, application denial, customer service, disclosure, fees, fraud and loan repayment. Your response strictly only consists of the category label. 

    # Category descriptions

    1. Advertising: Complaints pertaining to instances where consumers allege misleading or deceptive advertising by financial entities, such as in relation to promotional offers or terms (e.g., interest rates, rewards, or fees).
    2. Account closure: Complaints involving the unexpected or unjustified closure of consumer accounts or lines of credit by financial entities, often without sufficient notice or explanation, which may adversely impact credit scores or access to funds.
    3. Application denial: Complaints relating to cases where consumers claim they have been unjustly or improperly denied access to financial products (e.g., credit cards, loans, or accounts), often citing insufficient explanations, outdated or inaccurate data, and a lack of transparency in the denial process.
    4. Customer service: Complaints focusing on unsatisfactory customer support experiences, including allegations of prolonged response times, repeated procedural failures, unhelpful or contradictory guidance, and unresolved issues that hinder consumers from accessing or managing their financial accounts effectively.
    5. Disclosure: Complaints pertaining to situations where financial entities fail to clearly disclose key terms, fees, restrictions, or conditions, leading consumers to experience unexpected charges, hidden penalties, or delayed access to funds.
    6. Fees: Complaints pertaining to instances where consumers allege unfair or undisclosed fees imposed by financial entities, often contradicting stated terms or promotional assurances, and resulting in unexpected charges or financial harm.
    7. Fraud: Complaints pertaining to instances where consumers allege fraudulent or unauthorized transactions, identity theft, or deceptive tactics used by third parties or financial institutions, resulting in financial loss or unauthorized access to their accounts.
    8. Loan repayment: Complaints highlighting consumers’ difficulties with their loan repayment obligations such as unaffordable payments, ballooning interest, misapplied payments, or lack of adequate support or clear communication from loan servicers.

    # Output Format
    Your response strictly consists of the category label only, without any additional commentary.

    # Examples

    ## Example 1
    Consumer complaint: I was promised a 0% introductory APR for 12 months on my new credit card from Entity A. However, when I received my first statement, it already included a finance charge of $35.00. Despite multiple calls, they refuse to provide proof that the promotional period has ended.
    Assistant response: Advertising

    ## Example 2
    Consumer complaint: Two days ago, I attempted to use my card at the grocery store, and it was declined. When I called, they informed me the account was closed for inactivity. I never received an email or letter, and as a retiree, I rely on consistent credit availability for emergencies. This closure without warning has put me in a difficult spot.
    Assistant response: Account closure

    ## Example 3
    Consumer complaint: When I applied for a store-branded credit card from Entity S, I was declined on the basis of too many recent changes in my credit profile. In reality, the only major change was closing an old account I no longer used. Their denial letter didn’t specify what they found alarming, and repeated calls to their hotline yielded no additional insights. I believe this decision was based on outdated or incomplete data.
    Assistant response: Application denial

    ## Example 4
    Consumer complaint: I tried to enroll in online bill pay, but every time I log in, the screen freezes and tells me to contact support. Each agent I speak with gives me a different set of steps to fix the issue, none of which work. At this point, my bills are overdue, and I'm frustrated by the lack of a clear solution.
    Assistant response: Customer service

    ## Example 5
    Consumer complaint: My partner and I opened a joint checking account at Entity R, enticed by promises of fee-free bill payments. Unfortunately, we later discovered a hefty charge whenever payments exceeded a certain monthly threshold. None of this was spelled out in any of the materials we reviewed before signing up. We believe the bank should disclose all transaction limitations and associated fees up front, not hide them in vague terms.
    Assistant response: Disclosure

    ## Example 6
    Consumer complaint: Upon reviewing my most recent statement, I discovered a $60 'setup fee' attached to my new savings account. I had been told this account would have no fees if I met the minimum deposit requirement. The disclosure documents are unclear, and each customer service agent I speak to has a different story about why this fee was added.
    Assistant response: Fees

    ## Example 7
    Consumer complaint: I was asked to provide my account and routing numbers for a direct deposit bonus from a supposed 'employer.' They disappeared with my funds, and my bank claims there's no recourse because I willingly shared my details.
    Assistant response: Fraud

    ## Example 8
    Consumer complaint: I tried to enroll in an income-driven repayment plan, but Entity F delayed my application for months without explanation. In the meantime, they continued charging the standard rate, which is completely unaffordable given my current income. After multiple calls, I finally got a partial forbearance, but that only added more interest. Nobody explained the long-term consequences of these measures. I’m drowning in debt while waiting for them to finalize my paperwork.
    Assistant response: Loan repayment
    """
