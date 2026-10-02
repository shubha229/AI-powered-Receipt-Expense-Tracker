import json

import streamlit as st
from google import genai
from google.genai import types

from prompts import (
    RECEIPT_SYSTEM_PROMPT,
    RECEIPT_EXTRACTION_PROMPT,
    EXPENSE_ASSISTANT_SYSTEM_PROMPT,
    EXPENSE_ASSISTANT_PROMPT,
)


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing from .streamlit/secrets.toml"
    )


# Gemini 3.1 Flash-Lite is a stable, multimodal model
# optimized for speed, scale and cost efficiency.
MODEL_NAME = "gemini-3.1-flash-lite"

client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(
        timeout=20000
    ),
)


# ============================================================
# COMMON GENERATION FUNCTION
# ============================================================

def generate_content(contents, system_instruction):

    try:

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=contents,

            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
            ),
        )

        return response

    except Exception as error:

        message = str(error)

        if "503" in message or "UNAVAILABLE" in message.upper():

            raise RuntimeError(
                "Gemini is temporarily overloaded (503). "
                "Please wait a few seconds and try again."
            ) from error

        if "429" in message or "RESOURCE_EXHAUSTED" in message.upper():

            raise RuntimeError(
                "Gemini rate limit reached. "
                "Please wait and try again."
            ) from error

        if "404" in message or "NOT_FOUND" in message.upper():

            raise RuntimeError(
                f"Gemini model '{MODEL_NAME}' is not available "
                "for this API key."
            ) from error

        raise


# ============================================================
# RECEIPT ANALYSIS
# ============================================================

def extract_receipt(image):

    try:

        response = generate_content(
            contents=[
                RECEIPT_EXTRACTION_PROMPT,
                image,
            ],
            system_instruction=RECEIPT_SYSTEM_PROMPT,
        )

        text = response.text.strip()

        # Handle accidental Markdown JSON fences.
        if text.startswith("```"):

            if text.startswith("```json"):
                text = text[len("```json"):]

            else:
                text = text[len("```"):]

            if text.endswith("```"):
                text = text[:-3]

            text = text.strip()

        result = json.loads(text)

        if not isinstance(result, dict):

            return {
                "error": "Gemini returned an invalid receipt response."
            }

        return result

    except json.JSONDecodeError as error:

        return {
            "error": (
                "Gemini returned invalid JSON. "
                f"Details: {error}"
            )
        }

    except Exception as error:

        return {
            "error": str(error)
        }


# ============================================================
# EXPENSE AI ASSISTANT
# ============================================================

def ask_expense_ai(question, expenses):

    expense_data = []

    for expense in expenses:

        expense_data.append(
            {
                "date": expense.get("date"),
                "merchant": expense.get("merchant"),
                "amount": expense.get("amount"),
                "category": expense.get("category"),
                "paymentMethod": expense.get("paymentMethod"),
            }
        )

    task_prompt = EXPENSE_ASSISTANT_PROMPT.format(
        question=question,
        expense_data=json.dumps(
            expense_data,
            indent=2,
            default=str,
        ),
    )

    try:

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=task_prompt,

            config=types.GenerateContentConfig(
                system_instruction=EXPENSE_ASSISTANT_SYSTEM_PROMPT,
            ),
        )

        return response.text

    except Exception as error:

        return (
            "Unable to generate the AI response right now.\n\n"
            f"Details: {error}"
        )
