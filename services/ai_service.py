import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_suggestions(case_description, investigation_steps):

    logging.info(f"Generating suggestions for case: {case_description}")

    prompt = f"""
    You are a professional support engineer.

    Analyze the following support case.

    Suggest:
    - Possible root causes
    - Recommended next troubleshooting steps
    - Estimated severity

    Case Description:
    {case_description}

    Investigation Steps:
    {investigation_steps}
    """

    response = client.chat.completions.create(

        model="gpt-5-nano",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response.choices[0].message.content

    logging.info(f"AI response: {content}")

    return content

def improve_message(customer_message,case_description,investigation_steps):
    logging.info("Improving customer message")

    prompt = f"""
    You are a professional support engineer.

    Improve the following customer message.

    Customer Message:
    {customer_message}

    Case Description:
    {case_description}

    Investigation Steps:
    {investigation_steps}

    Make the message:
    - Professional
    - Friendly
    - Clear
    - Concise
    """

    response = client.chat.completions.create(
        model="gpt-5-mini",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response.choices[0].message.content

    logging.info("Message improved successfully")

    return content