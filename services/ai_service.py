import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

def get_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_suggestions(case_description: str, investigation_steps: str) -> str:
    logging.info("Generating suggestions for case: %s", case_description[:60])
    client = get_client()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional SAP Ariba support engineer "
                    "specialized in integration (API/EDI) and workflow issues."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Analyze the following support case and suggest:\n"
                    f"- Possible root causes\n"
                    f"- Recommended next troubleshooting steps\n"
                    f"- Estimated severity\n\n"
                    f"Case Description:\n{case_description}\n\n"
                    f"Investigation Steps Already Done:\n{investigation_steps}"
                ),
            },
        ],
    )

    content = response.choices[0].message.content
    logging.info("Suggestions generated successfully")
    return content


def improve_message(customer_message: str, tone: str, case_description: str, investigation_steps: str) -> str:
    logging.info("Improving customer message")

    client = get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional SAP Ariba support engineer "
                    "specialized in clear, empathetic customer communication."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Improve the following customer message. "
                    f"Make it professional, friendly, clear, and concise.\n\n"
                    f"Case Description:\n{case_description}\n\n"
                    f"Investigation Steps:\n{investigation_steps}\n\n"
                    f"Tone:\n{tone}\n\n"
                    f"Draft Message:\n{customer_message}"
                ),
            },
        ],
    )

    content = response.choices[0].message.content
    logging.info("Message improved successfully")
    return content
