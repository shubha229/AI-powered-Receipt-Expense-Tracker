import os
import hashlib
import secrets
import uuid
import json
import time
from datetime import date, datetime, timedelta
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from google import genai
from google.genai import types
from pymongo import MongoClient

# ============================================================
# SMARTSPEND
# AI Receipt & Expense Tracker
# IMPORTANT:
# This file intentionally uses ONLY native Streamlit UI.
# There is NO custom HTML/CSS/markdown HTML anywhere.
# Therefore \<div>, \<h1>, \<span>, etc. cannot appear as code.
# ============================================================

# ============================================================
# 1. ENVIRONMENT
# ============================================================

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "").strip()
MONGO_URI = st.secrets.get("MONGO_URI", "").strip()
TELEGRAM_BOT_TOKEN = st.secrets.get(
    "TELEGRAM_BOT_TOKEN", ""
).strip()
DEFAULT_TELEGRAM_CHAT_ID = st.secrets.get(
    "TELEGRAM_CHAT_ID", ""
).strip()

# ============================================================
# 2. PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SmartSpend",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 3. CONSTANTS
# ============================================================

CATEGORIES = [
    "Food",
    "Travel",
    "Shopping",
    "Bills",
    "Health",
    "Entertainment",
    "Education",
    "Other",
]

PAYMENT_METHODS = [
    "Cash",
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking",
    "Other",
]

# ============================================================
# 4. SESSION STATE
# ============================================================

SESSION_DEFAULTS = {
    "onboarded": False,
    "user_id": "",
    "user_name": "",
    "user_email": "",
    "telegram_chat_id": "",
    "receipt_data": None,
    "last_receipt": None,
}

for key, value in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

for key, value in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CUSTOM UI STYLING
# ============================================================

st.markdown(
    """
    <style>

    /* ============================================================
       LOGIN / ONBOARDING PAGE
       ============================================================ */

    /* Main onboarding background */
    .stApp {
        background: #f8fafc;
    }

    /* Centered onboarding content */
    .onboarding-container {
        max-width: 780px;
        margin: 40px auto 0 auto;
    }

    /* Brand title */
    .onboarding-brand {
        text-align: center;
        margin-bottom: 8px;
    }

    .onboarding-brand h1 {
        font-size: 42px !important;
        font-weight: 800 !important;
        letter-spacing: -1.5px;
        color: #111827 !important;
        margin-bottom: 4px !important;
    }

    .onboarding-tagline {
        text-align: center;
        font-size: 19px;
        font-weight: 600;
        color: #059669;
        margin-bottom: 8px;
    }

    .onboarding-description {
        text-align: center;
        color: #64748b;
        font-size: 14px;
        line-height: 1.6;
        max-width: 620px;
        margin: 0 auto 28px auto;
    }

    /* Login heading */
    .login-heading {
        text-align: center;
        color: #111827;
        font-size: 25px;
        font-weight: 750;
        margin-bottom: 4px;
    }

    .login-subheading {
        text-align: center;
        color: #64748b;
        font-size: 13px;
        margin-bottom: 22px;
    }

    /* Primary buttons */
    [data-testid="stBaseButton-primary"] {
        background: #10b981 !important;
        border: 1px solid #10b981 !important;
        border-radius: 10px !important;
        min-height: 44px !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stBaseButton-primary"]:hover {
        background: #059669 !important;
        border-color: #059669 !important;
        transform: translateY(-1px);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        gap: 8px;
        border-bottom: 1px solid #e5e7eb;
    }

    .stTabs [data-baseweb="tab"] {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #64748b !important;
        padding: 10px 18px !important;
    }

    .stTabs [aria-selected="true"] {
        color: #059669 !important;
    }

    /* Small footer */
    .onboarding-footer {
        text-align: center;
        color: #94a3b8;
        font-size: 12px;
        margin-top: 24px;
    }

    /* ============================================================
    SIDEBAR UI
    ============================================================ */

    /* Sidebar background */
    section[data-testid="stSidebar"] {
        background: #f8fafc !important;
        border-right: 1px solid #e2e8f0 !important;
    }

    /* Sidebar overall spacing */
    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }


    /* ============================================================
    SIDEBAR BRAND
    ============================================================ */

    section[data-testid="stSidebar"] h1 {
        font-size: 25px !important;
        font-weight: 800 !important;
        color: #111827 !important;
        letter-spacing: -0.5px !important;
    }

    section[data-testid="stSidebar"] h2 {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #1f2937 !important;
    }

    section[data-testid="stSidebar"] h3 {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #1f2937 !important;
    }


    /* ============================================================
    SIDEBAR NORMAL TEXT
    ============================================================ */

    section[data-testid="stSidebar"] p {
        font-size: 14px !important;
        color: #64748b !important;
        line-height: 1.5 !important;
    }


    /* ============================================================
    NAVIGATION TITLE
    ============================================================ */

    section[data-testid="stSidebar"]
    div[data-testid="stRadio"] > label {
        font-size: 13px !important;
        font-weight: 700 !important;
        color: #64748b !important;
        letter-spacing: 0.4px !important;
        text-transform: uppercase;
    }


    /* ============================================================
    NAVIGATION ITEMS
    ============================================================ */

    section[data-testid="stSidebar"]
    div[data-testid="stRadio"] label {
        font-size: 15px !important;
        font-weight: 550 !important;
        color: #334155 !important;
        padding: 8px 10px !important;
        margin: 3px 0 !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
    }


    /* Hover */
    section[data-testid="stSidebar"]
    div[data-testid="stRadio"] label:hover {
        background: #eaf7f2 !important;
        color: #047857 !important;
    }


    /* Selected navigation item */
    section[data-testid="stSidebar"]
    div[data-testid="stRadio"] label:has(input:checked) {
        background: #dff7ed !important;
        color: #047857 !important;
        font-weight: 700 !important;
        border-left: 3px solid #10b981 !important;
    }


    /* ============================================================
    SIDEBAR BUTTONS
    ============================================================ */

    section[data-testid="stSidebar"]
    div.stButton > button {
        width: 100% !important;
        min-height: 40px !important;
        border-radius: 10px !important;

        background: #ffffff !important;
        border: 1px solid #dbe2ea !important;

        color: #334155 !important;
        font-size: 14px !important;
        font-weight: 600 !important;

        transition: all 0.2s ease !important;
    }


    /* Button hover */
    section[data-testid="stSidebar"]
    div.stButton > button:hover {
        background: #ecfdf5 !important;
        border-color: #10b981 !important;
        color: #047857 !important;
    }


    /* ============================================================
    SIDEBAR INPUT
    ============================================================ */

    section[data-testid="stSidebar"]
    div[data-testid="stTextInput"] input {
        background: #ffffff !important;
        border: 1px solid #dbe2ea !important;
        border-radius: 10px !important;

        min-height: 40px !important;

        font-size: 14px !important;
        color: #1f2937 !important;
    }


    /* Input focus */
    section[data-testid="stSidebar"]
    div[data-testid="stTextInput"] input:focus {
        border-color: #10b981 !important;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.12) !important;
    }


    /* ============================================================
    SIDEBAR DIVIDERS
    ============================================================ */

    section[data-testid="stSidebar"] hr {
        border: none !important;
        border-top: 1px solid #e2e8f0 !important;

        margin-top: 18px !important;
        margin-bottom: 18px !important;
    }


    /* ============================================================
    SIDEBAR SUCCESS / INFO
    ============================================================ */

    section[data-testid="stSidebar"]
    div[data-testid="stAlert"] {
        border-radius: 10px !important;
        font-size: 13px !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 5. CONNECTIONS
# ============================================================

@st.cache_resource
def create_mongo_connection():
    if not MONGO_URI:
        return None, "MONGO_URI is missing from Streamlit secrets."

    try:
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=10000,
        )

        client.admin.command("ping")

        return client["smartspend"], None

    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"
    
@st.cache_resource
def create_gemini_connection():
    if not GEMINI_API_KEY:
        return None, "GEMINI_API_KEY is missing from Streamlit secrets.toml"

    try:
        client = genai.Client(
            api_key=GEMINI_API_KEY
        )
        return client, None

    except Exception as exc:
        return None, str(exc)

db, db_error = create_mongo_connection()
gemini_client, gemini_error = create_gemini_connection()

# IMPORTANT:
# PyMongo Database objects cannot be tested with `if db:`.
# Always use `db is not None`.

if db is not None:
    expenses_collection = db["expenses"]
    users_collection = db["users"]
    settings_collection = db["settings"]
    chat_history_collection = db["chat_history"]
else:
    expenses_collection = None
    users_collection = None
    settings_collection = None
    chat_history_collection = None

# ============================================================
# 6. BASIC HELPERS
# ============================================================

def money(value):
    try:
        return f"₹{float(value):,.2f}"
    except Exception:
        return "₹0.00"

def to_number(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default

def parse_date(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(
            str(value),
            "%Y-%m-%d",
        ).date()
    except Exception:
        return None

def month_expenses(expenses):
    today = date.today()
    result = []

    for expense in expenses:
        expense_date = parse_date(
            expense.get("date")
        )

        if (
            expense_date is not None
            and expense_date.month == today.month
            and expense_date.year == today.year
        ):
            result.append(expense)
    return result

def total_amount(expenses):
    return sum(
        to_number(expense.get("amount"))
        for expense in expenses
    )

def category_amounts(expenses):
    result = {}

    for expense in expenses:
        category = (
            expense.get("category")
            or "Other"
        )

        result[category] = (
            result.get(category, 0.0)
            + to_number(expense.get("amount"))
        )
    return result

# ============================================================
# 7. DATABASE FUNCTIONS
# ============================================================

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_bytes(16)
    elif isinstance(salt, str):
        salt = bytes.fromhex(salt)
    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return password_hash.hex(), salt.hex()

def verify_password(password, stored_hash, stored_salt):
    try:
        password_hash, _ = hash_password(password, stored_salt)
        return secrets.compare_digest(password_hash, stored_hash)
    except Exception:
        return False

def create_user(name, email, password):
    if users_collection is None:
        return False, "MongoDB is not connected."
    email = email.strip().lower(); name = name.strip()
    if users_collection.find_one({"email": email}):
        return False, "An account with this email already exists."
    password_hash, password_salt = hash_password(password)
    user_id = str(uuid.uuid4())
    document = {
        "user_id": user_id, "name": name, "email": email,
        "password_hash": password_hash, "password_salt": password_salt,
        "created_at": datetime.now(), "updated_at": datetime.now(),
    }
    try:
        users_collection.insert_one(document)
        return True, user_id
    except Exception as exc:
        return False, str(exc)

def authenticate_user(email, password):
    if users_collection is None:
        return None, "MongoDB is not connected."
    email = email.strip().lower()
    user = users_collection.find_one({"email": email})
    if user is None:
        return None, "No account found with this email."
    if not verify_password(password, user.get("password_hash", ""), user.get("password_salt", "")):
        return None, "Incorrect password."
    return user, None

def migrate_legacy_user_data(user_id, user_name):
    if expenses_collection is not None:
        expenses_collection.update_many(
            {"user": user_name, "user_id": {"$exists": False}},
            {"$set": {"user_id": user_id}},
        )
    if settings_collection is not None:
        settings_collection.update_many(
            {"user": user_name, "user_id": {"$exists": False}},
            {"$set": {"user_id": user_id}},
        )

def load_user_settings(user_id):
    if settings_collection is None:
        return {}
    return settings_collection.find_one({"user_id": user_id}) or {}

def save_user_settings(user_id, telegram_chat_id):
    if settings_collection is None:
        return False
    settings_collection.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, "telegram_chat_id": telegram_chat_id, "updated_at": datetime.now()}},
        upsert=True,
    )
    return True

def get_expenses():
    if expenses_collection is None:
        return []
    return list(expenses_collection.find({"user_id": st.session_state.user_id}).sort("created_at", -1))

def add_expense(expense):
    if expenses_collection is None:
        raise RuntimeError("MongoDB is not connected. Please check MONGO_URI.")
    document = dict(expense)
    document["user_id"] = st.session_state.user_id
    document["user"] = st.session_state.user_name
    document["created_at"] = datetime.now()
    expenses_collection.insert_one(document)
# ============================================================
# CHAT HISTORY
# ============================================================

def save_chat_message(question, answer):

    if chat_history_collection is None:
        return False

    chat_history_collection.insert_one({
        "user_id": st.session_state.user_id,
        "user": st.session_state.user_email,
        "question": question,
        "answer": answer,
        "created_at": datetime.now()
    })

    return True


def get_chat_history():

    if chat_history_collection is None:
        return []

    return list(
        chat_history_collection.find(
            {
                "user_id": st.session_state.user_id
            },
            {
                "_id": 0,
                "question": 1,
                "answer": 1,
                "created_at": 1
            }
        ).sort(
            "created_at",
            1
        )
    )


def clear_chat_history():

    if chat_history_collection is None:
        return False

    chat_history_collection.delete_many(
        {
            "user_id": st.session_state.user_id
        }
    )

    return True

def delete_expense(expense_id):
    if expenses_collection is None:
        return
    expenses_collection.delete_one({
        "_id": expense_id,
        "user_id": st.session_state.user_id,
    })

def get_budget():
    if settings_collection is None:
        return 0.0
    data = settings_collection.find_one({"user_id": st.session_state.user_id})
    if data is None:
        return 0.0
    return to_number(data.get("monthly_budget"))

def save_budget(amount):
    if settings_collection is None:
        raise RuntimeError("MongoDB is not connected. Please check MONGO_URI.")
    settings_collection.update_one(
        {"user_id": st.session_state.user_id},
        {"$set": {
            "user_id": st.session_state.user_id,
            "user": st.session_state.user_name,
            "monthly_budget": float(amount),
        }},
        upsert=True,
    )

# ============================================================
# 8. GEMINI RECEIPT ANALYSIS
# ============================================================

RECEIPT_SYSTEM_PROMPT = """
You are SmartSpend Receipt AI.
Analyze receipt images accurately.
Never invent information.
If information is missing or unclear, return null.
The final amount must be the actual final amount paid.
Do not confuse subtotal, tax, discount, or item prices
with the final amount.
Allowed expense categories:
Food, Travel, Shopping, Bills, Health,
Entertainment, Education, Other.
Return ONLY valid JSON.
"""
RECEIPT_EXTRACTION_PROMPT = """
Analyze the uploaded receipt image.
Extract:
1. Merchant/store name
2. Final total amount
3. Receipt date
4. Purchased items
5. Quantity of each item
6. Price of each item
7. Payment method if visible
8. Expense category
9. Notes if useful
Use this exact JSON structure:
{
    "merchant": "string or null",
    "amount": 0,
    "date": "YYYY-MM-DD or null",
    "category": "Food",
    "paymentMethod": "string or null",
    "items": [
        {
            "name": "string",
            "quantity": 1,
            "price": 0
        }
    ],
    "notes": "string or null"
}

Rules:
- Use the FINAL TOTAL.
- Do not use subtotal as the final amount.
- Do not use tax as the final amount.
- Do not use discount as the final amount.
- Do not guess missing values.
- Do not invent products or prices.
- Return ONLY JSON.
"""
def analyze_receipt(image_bytes, mime_type):
    if gemini_client is None:
        return {
            "error": gemini_error or "Gemini is not configured."
        }

    try:
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type,
        )
        models = [
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.6-flash",
            "gemini-3.5-flash",
        ]
        last_error = None
        for model_name in models:
           for attempt in range(2):
                try:
                    response = gemini_client.models.generate_content(
                        model=model_name,
                        config={
                            "system_instruction": RECEIPT_SYSTEM_PROMPT,
                        },
                        contents=[
                            RECEIPT_EXTRACTION_PROMPT,
                            image_part,
                        ],
                    )

                    text = (response.text or "").strip()
                    if text.startswith("```"):
                        text = text.replace("```json", "")
                        text = text.replace("```", "")
                        text = text.strip()
                    result = json.loads(text)

                    if not isinstance(result, dict):
                        return {
                            "error": "Gemini returned an invalid receipt format."
                        }
                    return result

                except Exception as e:
                    last_error = e
                    error_text = str(e)

                    # Retry temporary server/capacity errors
                    if (
                        "503" in error_text
                        or "UNAVAILABLE" in error_text
                        or "500" in error_text
                        or "INTERNAL" in error_text
                    ):
                        time.sleep(2 ** attempt)
                        continue

                    # Don't hide other errors
                    return {
                        "error": f"Receipt analysis failed: {e}"
                    }

        return {
            "error": (
                "Gemini models are temporarily unavailable. "
                f"Last error: {last_error}"
            )
        }

    except json.JSONDecodeError:
        return {
            "error": (
                "Gemini did not return valid JSON. "
                "Please try the receipt image again."
            )
        }

    except Exception as exc:
        return {
            "error": f"Receipt analysis failed: {exc}"
        }

# ============================================================
# 9. GEMINI EXPENSE ASSISTANT
# ============================================================

EXPENSE_SYSTEM_PROMPT = """
You are SmartSpend AI, an expense tracking assistant.
Use ONLY the expense data supplied in the prompt.

Never invent:
- expenses
- transactions
- amounts
- dates
- categories
- merchants
Use Indian Rupees (₹).
You can answer questions about:
- total spending
- monthly spending
- category spending
- average transaction
- highest expense
- transaction count
- budget
- remaining budget
- spending trends

Keep answers concise and accurate.
You are an expense tracking assistant,
not a financial advisor.
"""

def ask_expense_ai(question, expenses):
    """
    Answer simple expense questions locally.
    Use Gemini only for questions that require AI reasoning.
    """

    q = question.lower().strip()

    total = total_amount(expenses)
    monthly_expenses = month_expenses(expenses)
    monthly_total = total_amount(monthly_expenses)

    # ---------------------------------------------------------
    # 1. TOTAL SPENDING
    # ---------------------------------------------------------
    if (
        ("how much" in q or "total" in q)
        and ("spent" in q or "spending" in q or "expense" in q)
        and ("this month" not in q and "monthly" not in q)
    ):
        return f"You have spent {money(total)} in total."

    # ---------------------------------------------------------
    # 2. THIS MONTH'S SPENDING
    # ---------------------------------------------------------
    if (
        "this month" in q
        or "monthly spending" in q
        or "spent this month" in q
        or "spending this month" in q
    ):
        return (
            f"You have spent {money(monthly_total)} "
            f"this month across {len(monthly_expenses)} transaction(s)."
        )

    # ---------------------------------------------------------
    # 3. HIGHEST EXPENSE
    # ---------------------------------------------------------
    if (
        "highest expense" in q
        or "largest expense" in q
        or "biggest expense" in q
        or "most expensive" in q
    ):
        if not expenses:
            return "You don't have any recorded expenses yet."

        highest = max(
            expenses,
            key=lambda expense: to_number(expense.get("amount"))
        )

        merchant = highest.get("merchant", "Unknown")
        amount = to_number(highest.get("amount"))
        expense_date = highest.get("date", "-")

        return (
            f"Your highest expense was {money(amount)} "
            f"at {merchant} on {expense_date}."
        )

    # ---------------------------------------------------------
    # 4. MOST SPENT CATEGORY
    # ---------------------------------------------------------
    if (
        "category" in q
        and (
            "most" in q
            or "highest" in q
            or "more" in q
            or "spend the most" in q
        )
    ):
        categories = category_amounts(expenses)

        if not categories:
            return "You don't have any recorded expenses yet."

        category, amount = max(
            categories.items(),
            key=lambda item: item[1]
        )

        return (
            f"You spend the most on {category}, "
            f"with {money(amount)} spent."
        )

    # ---------------------------------------------------------
    # 5. TRANSACTION COUNT
    # ---------------------------------------------------------
    if (
        "how many" in q
        and (
            "transaction" in q
            or "expense" in q
            or "expenses" in q
        )
    ):
        return f"You have recorded {len(expenses)} transaction(s)."

    # ---------------------------------------------------------
    # 6. AVERAGE EXPENSE
    # ---------------------------------------------------------
    if (
        "average" in q
        and (
            "expense" in q
            or "spending" in q
            or "transaction" in q
        )
    ):
        if not expenses:
            return "You don't have any recorded expenses yet."

        average = total / len(expenses)

        return f"Your average transaction amount is {money(average)}."

    # ---------------------------------------------------------
    # 7. BUDGET
    # ---------------------------------------------------------
    if "budget" in q and "remaining" not in q:
        budget = get_budget()

        if budget <= 0:
            return "You haven't set a monthly budget yet."

        return f"Your monthly budget is {money(budget)}."

    # ---------------------------------------------------------
    # 8. REMAINING BUDGET
    # ---------------------------------------------------------
    if (
        "remaining budget" in q
        or "budget remaining" in q
        or "left in my budget" in q
        or "left in the budget" in q
    ):
        budget = get_budget()

        if budget <= 0:
            return "You haven't set a monthly budget yet."

        remaining = budget - monthly_total

        if remaining >= 0:
            return (
                f"You have {money(remaining)} remaining "
                f"from your monthly budget."
            )

        return (
            f"You are {money(abs(remaining))} over "
            f"your monthly budget."
        )

    # ---------------------------------------------------------
    # 9. NO EXPENSES
    # ---------------------------------------------------------
    if not expenses:
        return (
            "You don't have any recorded expenses yet. "
            "Add an expense or scan a receipt first."
        )

    # ---------------------------------------------------------
    # 10. USE GEMINI ONLY FOR AI-BASED QUESTIONS
    # ---------------------------------------------------------
    if gemini_client is None:
        return (
            "I can answer your expense calculations, "
            "but Gemini is currently unavailable for "
            "AI-based questions."
        )

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

    # ---------------------------------------------------------
    # COUNT EXPENSES IN A CATEGORY
    # ---------------------------------------------------------
    category_keywords = {
        "food": "Food",
        "travel": "Travel",
        "shopping": "Shopping",
        "bills": "Bills",
        "health": "Health",
        "entertainment": "Entertainment",
        "education": "Education",
        "other": "Other",
    }

    if (
        "how many" in q
        or "number of" in q
        or "count" in q
    ):
        for keyword, category_name in category_keywords.items():
            if keyword in q:
                count = sum(
                    1
                    for expense in expenses
                    if str(expense.get("category", "")).lower()
                    == category_name.lower()
                )

                return (
                    f"You have {count} "
                    f"{category_name} expense(s)."
                )

    prompt = f"""
    User question:
    {question}

    Recorded expense data:
    {json.dumps(
        expense_data,
        indent=2,
        default=str,
    )}

    Answer using only this data.

    Use ₹ for currency.
    Do not invent information.
    Keep the answer concise.
    """

    try:
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                response = gemini_client.models.generate_content(
                    model="gemini-3.8-flash",
                    config={
                        "system_instruction": EXPENSE_SYSTEM_PROMPT,
                    },
                    contents=prompt,
                )

                return response.text or "No response generated."

            except Exception as exc:
                error_text = str(exc)

                # Retry temporary Gemini overload/server errors
                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "500" in error_text
                    or "INTERNAL" in error_text
                ):
                    if attempt < max_attempts - 1:
                        wait_time = 2 ** attempt
                        time.sleep(wait_time)
                        continue

                return f"Unable to generate AI response: {exc}"

        return "Gemini is temporarily unavailable. Please try again."
    except Exception as exc:
        return (
            f"Unable to generate AI response: {exc}"
        )

# ============================================================
# 10. TELEGRAM
# ============================================================

def telegram_ready():
    return bool(
        TELEGRAM_BOT_TOKEN
        and
        st.session_state.telegram_chat_id
    )

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN:
        return (
            False,
            "TELEGRAM_BOT_TOKEN is missing in secrets.toml."
        )
    chat_id = (
        st.session_state.telegram_chat_id
    )

    if not chat_id:
        return (
            False,
            "Telegram Chat ID is missing."
        )

    url = (
        "https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    if len(message) > 3900:
        message = (
            message[:3900]
            + "\n\n...message truncated"
        )

    try:
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": message,
            },
            timeout=20,
        )

        data = response.json()

        if response.ok and data.get("ok"):
            return (
                True,
                "Telegram message sent successfully.",
            )

        return (
            False,
            data.get(
                "description",
                "Telegram message failed.",
            ),
        )

    except Exception as exc:
        return (
            False,
            f"Telegram error: {exc}",
        )

def build_receipt_telegram_message(receipt):
    merchant = (
        receipt.get("merchant")
        or "Unknown Merchant"
    )

    amount = to_number(
       receipt.get("amount")
    )

    receipt_date = (
        receipt.get("date")
        or "-"
    )

    category = (
        receipt.get("category")
        or "Other"
    )
    payment_method = (
        receipt.get("paymentMethod")
        or "Not available"
    )

    lines = [
        "🧾 SMARTSPEND RECEIPT SUMMARY",
        "",
        f"🏪 Merchant: {merchant}",
        f"💰 Final Amount: {money(amount)}",
        f"📅 Date: {receipt_date}",
        f"📂 Category: {category}",
        (
            "💳 Payment Method: "
            f"{payment_method}"
        ),
    ]

    items = receipt.get("items") or []

    if items:
        lines.extend(
            [
                "",
                "🛒 ITEMS",
            ]
        )

        for item in items:
            item_name = (
                item.get("name")
                or "Unknown Item"
            )

            quantity = item.get(
                "quantity",
                1,
            )

            price = to_number(
                item.get("price")
            )

            lines.append(
                f"• {item_name} × "
                f"{quantity} — {money(price)}"
            )

    notes = receipt.get("notes")

    if notes:
        lines.extend(
            [
                "",
                f"📝 Notes: {notes}",
            ]
        )

    lines.extend(
        [
            "",
            "🤖 Sent from SmartSpend",
        ]
    )
    return "\n".join(lines)

def build_monthly_telegram_message(
    expenses,
    budget,
):
    if not expenses:
        return (
            "💰 SMARTSPEND MONTHLY SUMMARY\n\n"
            "No expenses recorded this month."
        )

    total = total_amount(expenses)
    average = total / len(expenses)
    categories = category_amounts(
        expenses
    )
    highest = max(
        expenses,
        key=lambda item:
            to_number(item.get("amount")),
    )
    lines = [
        "💰 SMARTSPEND MONTHLY SUMMARY",
        "",
        f"💸 Total Expenses: {money(total)}",
        f"🧾 Transactions: {len(expenses)}",
        f"📊 Average Transaction: {money(average)}",
        "",
        (
            "🏆 Highest Expense: "
            f"{highest.get('merchant', 'Unknown')} — "
            f"{money(highest.get('amount'))}"
        ),
        "",
        "📂 CATEGORY BREAKDOWN",
    ]

    for category, amount in sorted(
        categories.items(),
         key=lambda item: item[1],
        reverse=True,
    ):
        lines.append(
            f"• {category}: {money(amount)}"
        )

    if budget > 0:
        remaining = budget - total
        used_percentage = (
            total / budget
        ) * 100

        lines.extend(
            [
                "",
                "🎯 BUDGET",
                f"Monthly Budget: {money(budget)}",
                f"Used: {used_percentage:.1f}%",
                f"Remaining: {money(remaining)}",
            ]
        )

    lines.extend(
        [
            "",
            "🤖 Sent from SmartSpend",
        ]
    )
    return "\n".join(lines)

# ============================================================
# 11. NATIVE STREAMLIT UI HELPERS
# ============================================================

def page_title(title, description):
    st.title(title)
    st.caption(description)

def show_connection_status():
    if db_error:
        st.sidebar.error(
            f"MongoDB connection failed:\n\n{db_error}"
        )

    if gemini_error:
        st.sidebar.warning(
            "Gemini is not configured."
        )

# ============================================================
# 12. CONNECTION STATUS
# ============================================================

show_connection_status()

# ============================================================
# 13. ONBOARDING
# ============================================================

if not st.session_state.onboarded:

    # --------------------------------------------------------
    # CENTER THE LOGIN CARD
    # --------------------------------------------------------

    left_space, center, right_space = st.columns(
        [1, 2, 1]
    )

    with center:

        # ----------------------------------------------------
        # BRAND
        # ----------------------------------------------------

        st.markdown(
            """
            <div class="onboarding-brand">
                <h1>💰 SmartSpend</h1>
            </div>

            <div class="onboarding-tagline">
                ✨ AI-powered personal finance
            </div>

            <div class="onboarding-description">
                Track expenses, scan receipts, manage your budget,
                analyze spending and receive smart financial insights
                — all in one place.
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------
        # LOGIN CARD
        # ----------------------------------------------------

        st.markdown(
            """
            <div class="login-heading">
                Welcome to SmartSpend
            </div>

            <div class="login-subheading">
                Sign in to continue managing your finances
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------
        # LOGIN / REGISTER TABS
        # ----------------------------------------------------

        login_tab, register_tab = st.tabs(
            [
                "🔐  Login",
                "📝  Create Account",
            ]
        )

        # ====================================================
        # LOGIN
        # ====================================================

        with login_tab:

            st.write("")

            login_email = st.text_input(
                "Email",
                placeholder="you@example.com",
                key="login_email",
            )

            login_password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password",
            )

            st.write("")

            if st.button(
                "Login  →",
                type="primary",
                use_container_width=True,
            ):

                if (
                    not login_email.strip()
                    or not login_password
                ):
                    st.warning(
                        "Please enter your email and password."
                    )

                else:

                    user, error = authenticate_user(
                        login_email,
                        login_password,
                    )

                    if error:

                        st.error(error)

                    else:

                        st.session_state.user_id = (
                            user["user_id"]
                        )

                        st.session_state.user_name = (
                            user["name"]
                        )

                        st.session_state.user_email = (
                            user["email"]
                        )

                        st.session_state.onboarded = True

                        migrate_legacy_user_data(
                            user["user_id"],
                            user["name"],
                        )

                        settings = load_user_settings(
                            user["user_id"]
                        )

                        st.session_state.telegram_chat_id = str(
                            settings.get(
                                "telegram_chat_id"
                            )
                            or ""
                        )

                        st.rerun()

        # ====================================================
        # CREATE ACCOUNT
        # ====================================================

        with register_tab:

            st.write("")

            register_name = st.text_input(
                "Full Name",
                placeholder="Enter your full name",
                key="register_name",
            )

            register_email = st.text_input(
                "Email",
                placeholder="you@example.com",
                key="register_email",
            )

            register_password = st.text_input(
                "Password",
                type="password",
                placeholder="Minimum 6 characters",
                key="register_password",
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter your password",
                key="confirm_password",
            )

            st.write("")

            if st.button(
                "Create Account  →",
                type="primary",
                use_container_width=True,
            ):

                email = register_email.strip().lower()

                if not register_name.strip():

                    st.warning(
                        "Please enter your name."
                    )

                elif not email or "@" not in email:

                    st.warning(
                        "Please enter a valid email address."
                    )

                elif len(register_password) < 6:

                    st.warning(
                        "Password must contain at least 6 characters."
                    )

                elif (
                    register_password
                    != confirm_password
                ):

                    st.error(
                        "Passwords do not match."
                    )

                else:

                    success, result = create_user(
                        register_name,
                        email,
                        register_password,
                    )

                    if not success:

                        st.error(result)

                    else:

                        st.session_state.user_id = result

                        st.session_state.user_name = (
                            register_name.strip()
                        )

                        st.session_state.user_email = (
                            email
                        )

                        st.session_state.onboarded = True

                        st.session_state.telegram_chat_id = ""

                        st.success(
                            "Account created successfully! 🎉"
                        )

                        st.rerun()

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        st.markdown(
            """
            <div class="onboarding-footer">
                🔒 Your expense data is securely stored
                in your personal SmartSpend account.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.stop()

# ============================================================
# 14. SIDEBAR
# ============================================================

with st.sidebar:

    # ========================================================
    # BRAND
    # ========================================================

    st.title("💰 SmartSpend")

    st.caption(
        f"Welcome, {st.session_state.user_name} 👋"
    )

    st.caption(
        st.session_state.user_email
    )

    st.divider()


    # ========================================================
    # LOGOUT
    # ========================================================

    if st.button(
        "🚪  Logout",
        use_container_width=True
    ):
        st.session_state.onboarded = False
        st.session_state.user_id = ""
        st.session_state.user_name = ""
        st.session_state.user_email = ""
        st.session_state.telegram_chat_id = ""
        st.session_state.receipt_data = None
        st.session_state.last_receipt = None
        st.rerun()


    st.divider()


    # ========================================================
    # NAVIGATION
    # ========================================================

    selected_page = st.radio(
        "NAVIGATION",
        [
            "🏠 Dashboard",
            "📸 Scan Receipt",
            "➕ Add Expense",
            "🧾 Expense History",
            "📊 Analytics",
            "🎯 Budget",
            "🤖 AI Assistant",
        ],
    )


    st.divider()


    # ========================================================
    # TELEGRAM
    # ========================================================

    st.subheader("📱 Telegram Settings")

    st.caption(
        "Connect Telegram to receive expense summaries."
    )

    telegram_chat_id = st.text_input(
        "Telegram Chat ID",
        value=str(
            st.session_state.telegram_chat_id
        ),
        placeholder="Enter Telegram Chat ID",
    )

    if st.button(
        "💾  Save Telegram Settings",
        use_container_width=True,
    ):

        st.session_state.telegram_chat_id = (
            telegram_chat_id.strip()
        )

        if save_user_settings(
            st.session_state.user_id,
            st.session_state.telegram_chat_id,
        ):
            st.success(
                "Telegram settings saved."
            )
        else:
            st.error(
                "Unable to save Telegram settings."
            )

    if telegram_ready():

        st.success(
            "Telegram is ready ✅"
        )

    else:

        st.info(
            "Add Telegram Chat ID to send messages."
        )
# ============================================================
# 15. LOAD DATA
# ============================================================

expenses = get_expenses()
current_month = month_expenses(
    expenses
)
budget = get_budget()
all_time_total = total_amount(
    expenses
)
monthly_total = total_amount(
    current_month
)

# ============================================================
# 16. DASHBOARD
# ============================================================

if selected_page == "🏠 Dashboard":
    page_title(
        "🏠 Dashboard",
        (
            "Your personal overview of expenses, "
            "budget and recent transactions."
        ),
    )

    metric_columns = st.columns(4)
    
    with metric_columns[0]:
        st.metric(
            "Total Spending",
            money(all_time_total),
        )
    
    with metric_columns[1]:
        st.metric(
            "This Month",
            money(monthly_total),
        )
    
    with metric_columns[2]:
        st.metric(
            "Transactions",
            len(expenses),
        )
    
    with metric_columns[3]:
        st.metric(
            "Monthly Budget",
            money(budget),
        )
    
    st.divider()
    
    chart_col, budget_col = st.columns(2)
    
    with chart_col:
        st.subheader(
            "📊 Spending by Category"
        )
        categories = category_amounts(
            expenses
        )
        if categories:
            chart_df = pd.DataFrame(
                {
                    "Category":
                        list(categories.keys()),
                    "Amount":
                        list(categories.values()),
                }
            )
            fig = px.pie(
                chart_df,
                names="Category",
                values="Amount",
                hole=0.5,
            )
            st.plotly_chart(
                fig,
                use_container_width=True,
            )
        else:
            st.info(
                "Add expenses to see category analytics."
            )
    
    with budget_col:
        st.subheader(
            "🎯 Monthly Budget"
        )
        if budget > 0:
            used = (
                monthly_total / budget
            ) * 100
            remaining = (
                budget - monthly_total
            )
            st.metric(
                "Spent This Month",
                money(monthly_total),
            )
            st.progress(
                min(used / 100, 1.0)
            )
            st.write(
                f"{used:.1f}% of your monthly budget used."
            )
            if remaining >= 0:
                st.success(
                    f"{money(remaining)} remaining."
                )
            else:
                st.error(
                    f"{money(abs(remaining))} over budget."
                )
        else:
            st.info(
                "Set a monthly budget from the Budget page."
            )
    
    st.divider()
    
    st.subheader(
        "🧾 Recent Transactions"
    )
    
    if expenses:
        for expense in expenses[:5]:
            with st.container(
                border=True
            ):
                left, right = st.columns(
                    [4, 1]
                )
                with left:
                    st.write(
                        f"**{expense.get('merchant', 'Unknown')}**"
                    )
                    st.caption(
                        f"{expense.get('category', 'Other')} "
                        f"• {expense.get('date', '-')}"
                    )
                with right:
                    st.metric(
                        "Amount",
                        money(
                            expense.get("amount")
                        ),
                    )
    
    else:
        st.info(
            "No expenses yet. Scan a receipt or add one manually."
        )

    
    st.divider()
    
    st.subheader(
        "📱 Telegram"
    )

    if st.button(
        "📊 Send Monthly Summary",
        use_container_width=True,
    ):

        if not telegram_ready():
            st.error(
                "Configure Telegram Chat ID first."
            )

        else:
            message = build_monthly_telegram_message(
                current_month,
                budget,
            )
            success, result = send_telegram_message(
                message
            )

            if success:
                st.success(result)
            else:
                st.error(result)

# ============================================================
# 17. SCAN RECEIPT
# ============================================================

elif selected_page == "📸 Scan Receipt":
    
    page_title(
        "📸 AI Receipt Scanner",
        (
            "Upload a receipt and Gemini will extract "
            "the merchant, final amount, date, items and category."
        ),
    )

    uploaded_file = st.file_uploader(
        "Upload receipt image",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp",
        ],
    )

    if uploaded_file:
        image_bytes = uploaded_file.getvalue()
        st.image(
            image_bytes,
            caption="Uploaded Receipt",
            width=500,
        )

        if st.button(
            "🤖 Analyze Receipt",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner(
                "Gemini is analyzing the receipt..."
            ):
                result = analyze_receipt(
                    image_bytes,
                    uploaded_file.type,
                )
            if "error" in result:
                st.error(
                    result["error"]
                )
            else:
                st.session_state.receipt_data = (
                    result
                )
                st.success(
                    "Receipt analyzed successfully!"
                )
    receipt = st.session_state.receipt_data

    if receipt:
        st.divider()
        st.subheader(
            "📝 Review Receipt Details"
        )

        merchant = st.text_input(
            "Merchant / Store",
            value=(
                receipt.get("merchant")
                or ""
            ),
        )
        amount = st.number_input(
            "Final Amount (₹)",
            min_value=0.0,
            value=to_number(
                receipt.get("amount")
            ),
            step=1.0,
        )

        extracted_date = (
            parse_date(
                receipt.get("date")
            )
            or date.today()
        )

        receipt_date = st.date_input(
            "Receipt Date",
            value=extracted_date,
        )

        extracted_category = (
            receipt.get("category")
            or "Other"
        )

        if extracted_category not in CATEGORIES:
            extracted_category = "Other"
        category = st.selectbox(
            "Category",
            CATEGORIES,
            index=CATEGORIES.index(
                extracted_category
            ),
        )

        extracted_payment = (
            receipt.get("paymentMethod")
            or "Other"
        )

        if extracted_payment not in PAYMENT_METHODS:
            extracted_payment = "Other"
        payment_method = st.selectbox(
            "Payment Method",
            PAYMENT_METHODS,
            index=PAYMENT_METHODS.index(
                extracted_payment
            ),
        )

        notes = st.text_area(
            "Notes",
            value=(
                receipt.get("notes")
                or ""
            ),
        )

        items = receipt.get("items") or []

        if items:
            st.subheader(
                "🛒 Purchased Items"
            )
            item_rows = []

            for item in items:
                item_rows.append(
                    {
                        "Item":
                            item.get("name")
                            or "Unknown",
                        "Quantity":
                            item.get("quantity", 1),
                        "Price":
                            to_number(
                                item.get("price")
                            ),
                    }
                )

            items_df = pd.DataFrame(
                item_rows
            )

            items_df["Price"] = (
                items_df["Price"]
                .map(money)
            )

            st.dataframe(
                items_df,
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        save_col, telegram_col = st.columns(2)

        def create_reviewed_receipt():
            return {
                "merchant":
                    merchant.strip(),
                "amount":
                    float(amount),
                "date":
                    receipt_date.isoformat(),
                "category":
                    category,
                "paymentMethod":
                    payment_method,
                "notes":
                    notes.strip(),
                "items":
                    items,
            }

        with save_col:
            if st.button(
                "💾 Save Receipt",
                type="primary",
                use_container_width=True,
            ):

                if not merchant.strip():
                    st.warning(
                        "Merchant is required."
                    )

                elif amount <= 0:
                    st.warning(
                        "Final amount must be greater than zero."
                    )

                else:
                    final_receipt = create_reviewed_receipt()
                    final_receipt["source"] = "receipt"
                    final_receipt["receipt_saved_at"] = datetime.now()
                    add_expense(final_receipt)
                    st.session_state.last_receipt = (
                        final_receipt
                    )
                    st.session_state.receipt_data = (
                        None
                    )
                    st.success(
                        "Receipt saved successfully! 🎉"
                    )
                    st.rerun()

        with telegram_col:
            if st.button(
                "📱 Save & Send to Telegram",
                use_container_width=True,
            ):
                if not merchant.strip():
                    st.warning(
                        "Merchant is required."
                    )
                elif amount <= 0:
                    st.warning(
                        "Final amount must be greater than zero."
                    )
                elif not telegram_ready():
                    st.error(
                        "Configure Telegram Chat ID first."
                    )
                else:
                    final_receipt = create_reviewed_receipt()
                    final_receipt["source"] = "receipt"
                    final_receipt["receipt_saved_at"] = datetime.now()
                    add_expense(final_receipt)
                    success, result = (
                        send_telegram_message(
                            build_receipt_telegram_message(
                                final_receipt
                            )
                        )
                    )
                    st.session_state.last_receipt = (
                        final_receipt
                    )
                    st.session_state.receipt_data = (
                        None
                    )

                    if success:
                        st.success(
                            "Receipt saved and "
                            "details sent to Telegram! 📱"
                        )
                    else:
                        st.warning(
                            "Receipt saved, but Telegram failed: "
                            + result
                        )
                    st.rerun()

# ============================================================
# 18. MANUAL ADD EXPENSE
# ============================================================

elif selected_page == "➕ Add Expense":
    page_title(
        "➕ Add Expense",
        "Record an expense manually.",
    )
    with st.form(
        "manual_expense_form",
        clear_on_submit=True,
    ):
        merchant = st.text_input(
            "Merchant / Description",
            placeholder="e.g. Amazon, Uber, Swiggy",
        )
        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=10.0,
        )
        expense_date = st.date_input(
            "Date",
            value=date.today(),
        )
        category = st.selectbox(
            "Category",
            CATEGORIES,
        )
        payment_method = st.selectbox(
            "Payment Method",
            PAYMENT_METHODS,
        )
        notes = st.text_area(
            "Notes",
        )
        submitted = st.form_submit_button(
            "Save Expense 💾",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not merchant.strip():
            st.warning(
                "Merchant is required."
            )
        elif amount <= 0:
            st.warning(
                "Amount must be greater than zero."
            )
        else:
            add_expense(
                {
                    "merchant":
                        merchant.strip(),
                    "amount":
                        float(amount),
                    "date":
                        expense_date.isoformat(),
                    "category":
                        category,
                    "paymentMethod":
                        payment_method,
                    "notes":
                        notes.strip(),
                    "items":
                        [],
                }
            )

            st.success(
                "Expense saved successfully! 🎉"
            )

            st.rerun()

# ============================================================
# 19. EXPENSE HISTORY
# ============================================================

elif selected_page == "🧾 Expense History":
    page_title(
        "🧾 Expense History",
        "Search, review and delete your recorded expenses.",
    )
    search = st.text_input(
        "🔍 Search expenses",
        placeholder=(
            "Search merchant, category or payment method"
        ),
    )
    filtered = expenses
    if search:
        query = search.lower()
        filtered = [
            expense
            for expense in expenses
            if (
                query
                in str(
                    expense.get(
                        "merchant",
                        "",
                    )
                ).lower()
                or
                query
                in str(
                    expense.get(
                        "category",
                        "",
                    )
                ).lower()
                or
                query
                in str(
                    expense.get(
                        "paymentMethod",
                        "",
                    )
                ).lower()
            )
        ]

    st.caption(
        f"{len(filtered)} transaction(s)"
    )

    if not filtered:
        st.info(
            "No expenses found."
        )

    else:
        for expense in filtered:
            with st.container(
                border=True
            ):
                col1, col2, col3 = st.columns(
                    [5, 2, 1]
                )
                with col1:
                    st.write(
                        f"**{expense.get('merchant', 'Unknown')}**"
                    )
                    st.caption(
                        f"{expense.get('category', 'Other')} "
                        f"• {expense.get('date', '-')}"
                    )

                with col2:
                    st.metric(
                        "Amount",
                        money(
                            expense.get("amount")
                        ),
                    )

                with col3:
                    expense_id = expense.get(
                        "_id"
                    )
                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_{expense_id}",
                    ):
                        delete_expense(
                            expense_id
                        )
                        st.rerun()

# ============================================================
# 20. ANALYTICS
# ============================================================

elif selected_page == "📊 Analytics":
    page_title(
        "📊 Analytics",
        "Explore your spending by category and over time.",
    )

    if not expenses:
        st.info(
            "Add expenses to see analytics."
        )
    else:
        categories = category_amounts(
            expenses
        )
        chart_df = pd.DataFrame(
            {
                "Category":
                    list(categories.keys()),
                "Amount":
                    list(categories.values()),
            }
        )
        left, right = st.columns(2)
        with left:
            st.subheader(
                "Category Spending"
            )
            bar_fig = px.bar(
                chart_df,
                x="Category",
                y="Amount",
                text_auto=".2f",
            )
            bar_fig.update_layout(
                yaxis_title="Amount (₹)"
            )
            st.plotly_chart(
                bar_fig,
                use_container_width=True,
            )
        with right:
            st.subheader(
                "Spending Distribution"
            )
            pie_fig = px.pie(
                chart_df,
                names="Category",
                values="Amount",
                hole=0.45,
            )
            st.plotly_chart(
                pie_fig,
                use_container_width=True,
            )
        st.subheader(
            "📈 Expense Timeline"
        )
        timeline_rows = []
        for expense in expenses:
            expense_date = parse_date(
                expense.get("date")
            )
            if expense_date:
                timeline_rows.append(
                    {
                        "Date":
                            expense_date,
                        "Amount":
                            to_number(
                                expense.get(
                                    "amount"
                                )
                            ),
                    }
                )

        if timeline_rows:
            timeline_df = pd.DataFrame(
                timeline_rows
            )
            daily_df = (
                timeline_df
                .groupby("Date")["Amount"]
                .sum()
                .reset_index()
            )
            line_fig = px.line(
                daily_df,
                x="Date",
                y="Amount",
                markers=True,
            )
            line_fig.update_layout(
                yaxis_title="Amount (₹)"
            )
            st.plotly_chart(
                line_fig,
                use_container_width=True,
            )

# ============================================================
# 21. BUDGET
# ============================================================
elif selected_page == "🎯 Budget":
    page_title(
        "🎯 Budget Management",
        "Set your monthly budget and monitor usage.",
    )
    new_budget = st.number_input(
        "Monthly Budget (₹)",
        min_value=0.0,
        value=float(budget),
        step=500.0,
    )
    if st.button(
        "Save Budget 💾",
        type="primary",
        use_container_width=True,
    ):
        save_budget(
            new_budget
        )
        st.success(
            "Monthly budget saved!"
        )
        st.rerun()
    st.divider()

    if new_budget > 0:
        used_percentage = (
            monthly_total / new_budget
        ) * 100
        remaining = (
            new_budget - monthly_total
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(
                "Monthly Budget",
                money(new_budget),
            )
        with c2:
            st.metric(
                "Spent",
                money(monthly_total),
            )
        with c3:
            st.metric(
                "Remaining",
                money(remaining),
            )
        st.progress(
            min(
                used_percentage / 100,
                1.0,
            )
        )
        st.write(
            f"{used_percentage:.1f}% of budget used."
        )

        if remaining >= 0:
            st.success(
                f"{money(remaining)} remaining."
            )
        else:
            st.error(
                f"{money(abs(remaining))} over budget."
            )
    else:
        st.info(
            "Set a monthly budget to start tracking it."
        )

# ============================================================
# 22. AI ASSISTANT
# ============================================================

elif selected_page == "🤖 AI Assistant":

    page_title(
        "🤖 SmartSpend AI",
        "Ask questions about your recorded expenses.",
    )

    st.info(
        "Examples: "
        "How much did I spend this month? "
        "What category do I spend the most on? "
        "What was my highest expense?"
    )

    # ========================================================
    # CHAT HISTORY CONTROLS
    # ========================================================

    chat_history = get_chat_history()

    col1, col2 = st.columns([5, 1])

    with col1:
        st.markdown(
            "### 💬 Chat History"
        )

    with col2:
        if st.button(
            "🗑️ Clear",
            use_container_width=True
        ):
            if clear_chat_history():
                st.success(
                    "Chat history cleared."
                )
                st.rerun()

    # ========================================================
    # DISPLAY CHAT HISTORY
    # ========================================================

    if chat_history:

        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        today_chats = []
        yesterday_chats = []
        previous_chats = []

        for chat in chat_history:

            created_at = chat.get("created_at")

            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(
                        created_at
                    )
                except:
                    created_at = None

            if created_at:

                chat_date = created_at.date()

                if chat_date == today:
                    today_chats.append(chat)

                elif chat_date == yesterday:
                    yesterday_chats.append(chat)

                else:
                    previous_chats.append(chat)

        # ----------------------------------------------------
        # TODAY
        # ----------------------------------------------------

        if today_chats:

            st.markdown("#### 📅 Today")

            for chat in today_chats:

                with st.chat_message("user"):
                    st.write(chat["question"])

                with st.chat_message("assistant"):
                    st.write(chat["answer"])

        # ----------------------------------------------------
        # YESTERDAY
        # ----------------------------------------------------

        if yesterday_chats:

            st.markdown("#### 🕐 Yesterday")

            for chat in yesterday_chats:

                with st.chat_message("user"):
                    st.write(chat["question"])

                with st.chat_message("assistant"):
                    st.write(chat["answer"])

        # ----------------------------------------------------
        # PREVIOUS CONVERSATIONS
        # ----------------------------------------------------

        if previous_chats:

            st.markdown(
                "#### 📚 Previous Conversations"
            )

            for chat in previous_chats:

                with st.chat_message("user"):
                    st.write(chat["question"])

                with st.chat_message("assistant"):
                    st.write(chat["answer"])

    else:

        st.empty()

        st.info(
            "No chat history yet. Start a conversation with SmartSpend AI!"
        )

    # ========================================================
    # NEW QUESTION
    # ========================================================

    question = st.chat_input(
        "Ask about your expenses..."
    )

    if question:

        # Show user's question immediately
        with st.chat_message("user"):
            st.write(question)

        # Generate AI response
        with st.chat_message("assistant"):

            with st.spinner(
                "Analyzing your expenses..."
            ):

                answer = ask_expense_ai(
                    question,
                    expenses,
                )

            st.write(answer)

        # Save conversation to MongoDB
        save_chat_message(
            question,
            answer
        )

# ============================================================
# 23. FOOTER
# ============================================================

st.divider()
st.caption(
    "SmartSpend 💰 • AI-powered receipt and expense tracking"
)