# BudgetMind: AI Cashflow Forecaster & Crisis Advisor 💸

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Gemini API](https://img.shields.io/badge/Google-Gemini%201.5%20Pro-8E75B2?logo=google&logoColor=white)](https://ai.google.dev/)

**BudgetMind** is a "CFO in a Box" designed specifically for Small and Medium Enterprises (SMEs). Standard accounting software only records history—BudgetMind looks forward. It connects to financial data to predict cash shortfalls up to 90 days in advance and leverages **Google's Gemini AI** to explain *why* a crisis is looming and suggest actionable, context-aware strategies to avoid it.

---

## 🚀 The Problem & Solution

**The Problem:** 82% of businesses fail due to poor cash flow management, not a lack of profit. Small business owners are experts in their trade, not finance, and struggle to run complex "what-if" scenarios while managing fragmented data.
**The Solution:** A predictive web-based dashboard where users can upload simple financial records. BudgetMind aggregates the data, runs predictive simulations, forecasts cash flow drops, and presents tailored AI survival strategies to safely navigate around a sub-zero cash crunch.

## ✨ Key Features

1. **Predictive Cashflow Visuals:** Interactive graphs forecasting your "Projected Cash Balance" against safe operating threshold levels.
2. **AI-Powered Crisis Advisor:** Uses **Gemini 1.5 Pro** to analyze financial topologies, pinpointing exact causes of impending shortfalls (e.g., late clients paired with upcoming large payments).
3. **Decision Simulator (What-If Analysis):** Input hypothetical scenarios (e.g., "What if I hire a new developer for $4000/month?") to instantly see how this impacts your financial runway.
4. **Actionable Recommendations:** Get context-specific solutions like offering an early payment discount, managing vendor terms, or slicing specific expenses.
5. **Dumb vs. Smart Mode:** Toggle AI explanations off to see only raw calculations or run in "Crisis Mode" to experience a simulated financial drop.

## 🛠️ Architecture

* **Frontend:** Streamlit (Dynamic interactive dashboard)
* **Data Processing:** Pandas & NumPy (Data aggregation, running balance calculations)
* **Visualization:** Altair (Time-series line charts with threshold rules)
* **AI/Logic Layer:** Python + Google Generative AI SDK, powered by **Gemini 1.5 Pro** utilizing system instructions.

## 📁 Repository Structure

```text
├── app.py                     # Main Streamlit dashboard application
├── BudgetMind.md              # Original project spec and hackathon notes
├── sample_financial_data.csv  # Mock CSV financial data to use
├── core/
│   ├── forecaster.py          # Data ingestion, cleaning, and financial math logic
│   └── gemini_client.py       # Integration with the Google Gemini API
├── prompts/
│   ├── system_prompt.py             # Base system instructions for Gemini
│   └── decision_simulator_prompt.py # Prompts for What-If NLP analysis
└── utils/
    └── data_generator.py      # Script to generate synthetic test data
```

## ⚙️ How to Run Locally

### 1. Prerequisites

Ensure you have Python 3.10+ installed. Obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/).

### 2. Setup your Environment

Clone the repository and install the required dependencies:

```bash
# Clone the repo
git clone https://github.com/yourusername/BudgetMind.git
cd BudgetMind

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS and Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install streamlit pandas altair google-generativeai
```

### 3. Configure API Key

You can export the Gemini API key to your environment variables or enter it directly in the UI later:

```bash
# On macOS and Linux:
export GEMINI_API_KEY="your-google-gemini-api-key"

# On Windows (Command Prompt):
set GEMINI_API_KEY="your-google-gemini-api-key"

# On Windows (PowerShell):
$env:GEMINI_API_KEY="your-google-gemini-api-key"
```

### 4. Run the Application

Start the Streamlit application using:

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

## 📊 Using the App

* When opened, use the sidebar to **Upload Financial Data** (`sample_financial_data.csv`), or turn on the **Crisis Mode** toggle to see a built-in risky scenario.

* Input your **Gemini API Key** in the sidebar (if you haven't set it via the CLI).
* Read through the "6-Month Projected Balance" and interact with the "Running Balance Over Time" graph.
* Scroll down to review the AI Crisis Report explaining where the financial drops happen and how to avoid running out of cash!

---

*Built for UMHackathon 2026.*
