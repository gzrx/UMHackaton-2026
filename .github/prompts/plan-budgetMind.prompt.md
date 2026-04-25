## Plan: BudgetMind Architecture & Strategy

**TL;DR** 
A modular Streamlit application architecture for BudgetMind, centralizing data processing and AI logic, ensuring separation of concerns. The tool will strictly parse simple CSVs, calculate running balances, and interact with the Gemini API via the official `google-generativeai` SDK to provide actionable financial advice.

**Steps**
1. Initialize the project repository and virtual environment.
2. Generate mock datasets (`utils/data_generator.py`), including a standard baseline and a "Crisis Mode" dataset.
3. Define the configuration module (`core/config.py`) to manage API credentials securely.
4. Implement the data processing module (`core/forecaster.py`) to handle simple CSV ingestion, running balance calculation, anomaly detection, and "what-if" scenario injection.
5. Implement the LLM integration module (`core/gemini_client.py`) utilizing the chosen SDK for crisis explanations and JSON parameter extraction (Decision Simulator).
6. Develop the Streamlit frontend (`app.py` and `src/components/`) featuring interactive charts, Decision Simulator input, and UI toggles for Crisis/Dumb Mode.

**Relevant files**
- `app.py` — Main entry point. Handles UI toggles (Crisis/Dumb Mode) and the Decision Simulator text input.
- `core/config.py` — Configuration settings and secret management.
- `core/forecaster.py` — Running balances, anomaly detection logic, and injecting hypothetical scenario rows.
- `core/gemini_client.py` — Prompt building, JSON extraction for simulations, and narrative AI advice.
- `utils/data_generator.py` — Script to generate synthetic baseline and crisis CSVs (fulfills Hour 1-2 requirement).
- `requirements.txt` — Project dependencies securely pinned.

**Verification**
1. Run local Streamlit server and upload a test CSV to ensure columns are recognized.
2. Verify daily running balance logic against a known manual calculation.
3. Ping the Gemini API with mock negative balance data and assert a valid response is returned.

**Decisions**
- Use official `google-generativeai` SDK for easier prompt management.
- Strictly enforce simple CSV formats for now.
- Isolate the data processing logic entirely from Streamlit so it can easily be migrated to a backend service like FastAPI in the future.
- Use explicit configuration classes rather than pulling `os.getenv` randomly across files for better security audits.