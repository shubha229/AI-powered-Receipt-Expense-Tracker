# 💰 SmartSpend — AI-Powered Receipt & Expense Tracker

SmartSpend is an AI-powered personal finance application that helps users record, analyze, and manage their daily expenses.

## 🚀 Features

- 🔐 User authentication with hashed passwords
- 🧾 AI-powered receipt scanning using Google Gemini
- 💸 Manual expense management
- 📊 Dashboard with spending summaries
- 📈 Interactive analytics using Plotly
- 🎯 Monthly budget management
- 🤖 AI expense assistant
- 💬 Persistent AI chat history stored in MongoDB
- 📱 Telegram receipt and monthly expense summaries
- 👤 User-specific data isolation

## 🧾 AI Receipt Scanner

Upload a receipt image and Gemini AI can extract:

- Merchant / store name
- Final amount
- Receipt date
- Purchased items
- Quantity
- Item prices
- Payment method
- Expense category
- Notes

The extracted information can be reviewed and edited before saving.

### Receipt Flow

```text
Receipt Image
      ↓
Google Gemini AI
      ↓
Information Extraction
      ↓
Review & Edit
      ↓
MongoDB
      ↓
Expense Dashboard
```

## 💸 Expense Management

Users can add expenses manually or by scanning receipts.

### Categories

- Food
- Travel
- Shopping
- Bills
- Health
- Entertainment
- Education
- Other

### Payment Methods

- Cash
- UPI
- Credit Card
- Debit Card
- Net Banking
- Other

## 📊 Dashboard

The dashboard provides:

- Total spending
- Current month spending
- Number of transactions
- Monthly budget
- Spending by category
- Budget utilization
- Recent transactions
- Telegram monthly summary

## 📈 Analytics

Interactive Plotly charts help analyze:

- Category-wise spending
- Total spending
- Monthly spending
- Transaction patterns
- Expense distribution

## 🎯 Budget Management

Users can set a monthly spending budget.

SmartSpend calculates:

- Monthly budget
- Amount spent
- Percentage of budget used
- Remaining budget
- Amount over budget

Example:

```text
Monthly Budget: ₹20,000
Spent:          ₹14,500
Remaining:      ₹5,500
Used:           72.5%
```

## 🤖 AI Expense Assistant

The AI assistant can answer questions such as:

```text
How much did I spend?
How much did I spend this month?
Which category did I spend the most on?
What was my highest expense?
What is my average expense?
What is my monthly budget?
How much budget do I have remaining?
How many expenses do I have?
How many bills are present?
```

Simple financial calculations can be handled locally using Python, reducing unnecessary Gemini API requests.

## 💬 Persistent AI Chat History

SmartSpend stores AI conversations in MongoDB.

History is organized into:

- 📅 Today
- 🕐 Yesterday
- 📚 Previous Conversations

Users can clear their chat history. Each user's history is isolated using their unique `user_id`.

## 📱 Telegram Integration

SmartSpend can send receipt information and monthly spending summaries through Telegram.

## 🛠️ Tech Stack

### Frontend / UI
- Streamlit

### Programming Language
- Python

### AI
- Google Gemini API
- `google-genai`

### Database
- MongoDB Atlas
- PyMongo

### Data Analysis
- Pandas
- Plotly

### Image Processing
- Pillow

### Communication
- Telegram Bot API
- Requests

### Development
- Git
- GitHub
- VS Code

## 🏗️ System Architecture

```text
                       ┌──────────────────────┐
                       │        User          │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │     Streamlit UI     │
                       └──────────┬───────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
       ┌────────────┐      ┌────────────┐      ┌─────────────┐
       │   Receipt  │      │  Expenses  │      │ AI Assistant│
       │   Scanner  │      │ Management │      │             │
       └─────┬──────┘      └─────┬──────┘      └──────┬──────┘
             │                   │                     │
             ▼                   │                     ▼
       ┌────────────┐            │             ┌──────────────┐
       │ Gemini AI  │            │             │ Gemini API   │
       └─────┬──────┘            │             └──────┬───────┘
             │                   │                    │
             └───────────────────┼────────────────────┘
                                 ▼
                       ┌──────────────────────┐
                       │     MongoDB Atlas    │
                       │ users / expenses     │
                       │ settings / history   │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │   Telegram Bot API   │
                       └──────────────────────┘
```

## 📂 Project Structure

```text
Receipt&ExpenseTracker/
│
├── .streamlit/
│   └── secrets.toml
│
├── app.py
├── database.py
├── expense_service.py
├── gemini_service.py
├── prompts.py
├── telegram_service.py
│
├── requirements.txt
├── README.md
├── .gitignore
│
└── venv/
```

> `.streamlit/secrets.toml` and `venv/` should never be committed to GitHub.

## 🗄️ MongoDB Database Structure

Database:

```text
smartspend
```

Collections:

```text
smartspend
├── users
├── expenses
├── settings
└── chat_history
```

### Users

Stores account information including a hashed password.

### Expenses

Stores user-specific expense records.

### Settings

Stores user-specific settings such as monthly budget and Telegram configuration.

### Chat History

Stores:

- `user_id`
- `question`
- `answer`
- `created_at`

## 🔐 Configuration

Create:

```text
.streamlit/secrets.toml
```

Add:

```toml
GEMINI_API_KEY = "your_gemini_api_key"
MONGO_URI = "your_mongodb_connection_string"
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
TELEGRAM_CHAT_ID = "your_telegram_chat_id"
```

### ⚠️ Security

Never upload `.streamlit/secrets.toml` to GitHub.

Recommended `.gitignore`:

```gitignore
.streamlit/secrets.toml
.env
venv/
.venv/
__pycache__/
*.pyc
.vscode/
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/shubha229/AI-powered-Receipt-Expense-Tracker.git
```

### 2. Open the project

```bash
cd AI-powered-Receipt-Expense-Tracker
```

### 3. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate:

```powershell
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## ▶️ Run the Application

```bash
streamlit run app.py
```

The application will open in your browser.

## 🔑 Required Services

### Google Gemini
Used for receipt image analysis and AI expense questions.

### MongoDB Atlas
Used for user accounts, expenses, settings, and chat history.

### Telegram Bot
Used for receipt and monthly expense summaries.

## 🔄 Application Workflow

### User Registration

```text
Create Account
      ↓
Password Hashing
      ↓
MongoDB Users Collection
      ↓
SmartSpend Dashboard
```

### Login

```text
Email + Password
      ↓
Verify Password Hash
      ↓
Load User Settings
      ↓
Dashboard
```

### Receipt Scanning

```text
Upload Receipt
      ↓
Gemini Vision Analysis
      ↓
Extract Receipt Data
      ↓
Review / Edit
      ↓
Save Expense
      ↓
MongoDB
```

### AI Assistant

```text
User Question
      ↓
Local Expense Calculation
      │
      ├── Simple Query ──→ Python Result
      │
      └── AI Query ──────→ Gemini
                              ↓
                         AI Response
                              ↓
                      MongoDB Chat History
```

## 🛡️ Security

SmartSpend implements:

- PBKDF2-HMAC-SHA256 password hashing
- Random password salts
- User-specific database queries
- Secrets stored outside source code
- `.gitignore` protection for credentials
- User-specific chat history
- User-specific expenses
- Secure MongoDB connection

## 🚧 Future Enhancements

- 📤 Export expenses to CSV/PDF
- 📅 Advanced date-based filtering
- 📊 More advanced analytics
- 📈 Spending trend predictions
- 🔔 Budget alerts
- 🤖 More intelligent expense insights
- 🔎 Advanced expense search
- 📱 Enhanced Telegram automation
- ☁️ Production deployment
- 🧾 Improved receipt OCR and validation
- 📱 Further mobile UI improvements

## 🎯 Project Objectives

1. Simplify personal expense tracking.
2. Reduce manual receipt data entry.
3. Use AI to extract structured information from receipts.
4. Provide meaningful spending insights.
5. Help users monitor monthly budgets.
6. Provide persistent and user-specific expense data.
7. Integrate messaging through Telegram.
8. Demonstrate practical integration of AI, databases, and web applications.

## 💡 Key Learning Outcomes

- Python application development
- Streamlit application development
- Generative AI integration
- Gemini API usage
- Image-based AI processing
- MongoDB database integration
- CRUD operations
- Authentication
- Password hashing
- User-specific data isolation
- Data visualization
- Budget calculations
- Telegram Bot API integration
- Git and GitHub
- Secrets management

## 👩‍💻 Author

**Shubhashree Nayak**

Computer Science Engineering Student

GitHub: https://github.com/shubha229

## 📜 License

This project is developed for educational and portfolio purposes.
