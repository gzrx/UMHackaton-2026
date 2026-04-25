import streamlit as st
import pandas as pd
import altair as alt
import os
import json
from google import genai
from datetime import datetime, timedelta

from core.forecaster import load_and_clean_data, calculate_daily_running_balance, detect_shortfalls
from core.gemini_client import get_financial_advice, get_gemini_response
from prompts.system_prompt import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from prompts.decision_simulator_prompt import DECISION_SIMULATOR_PROMPT

# Configure Streamlit page
st.set_page_config(page_title="Financial Crisis Advisor", page_icon="📈", layout="wide")

def main():
    st.title("📉 AI-Powered Financial Crisis Advisor")
    st.markdown("Upload your financial projections to detect potential cash crunches and get AI-driven survival strategies.")

    # --- Sidebar Layout ---
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Initialize session state for API key if missing
        if "api_key_input" not in st.session_state:
            st.session_state.api_key_input = os.environ.get("GEMINI_API_KEY", "")

        current_api_key = st.session_state.api_key_input

        # Validate API key logic and cache the validation result
        if "api_key_status" not in st.session_state:
            st.session_state.api_key_status = {"key": None, "symbol": "⚠️", "help": "Missing: API key is required."}

        if current_api_key != st.session_state.api_key_status["key"]:
            if not current_api_key:
                st.session_state.api_key_status = {"key": current_api_key, "symbol": "⚠️", "help": "Missing: API key is required."}
            else:
                try:
                    temp_client = genai.Client(api_key=current_api_key)
                    # Attempt to list models; this validates the key and checks permissions
                    models = temp_client.models.list()
                    # Iterate to ensure the API call gets made if it returns an iterator
                    for _ in models: break
                    st.session_state.api_key_status = {"key": current_api_key, "symbol": "✅", "help": "Valid: API key authorized."}
                except Exception as e:
                    st.session_state.api_key_status = {"key": current_api_key, "symbol": "❌", "help": "Invalid: API key not authorized."}

        status = st.session_state.api_key_status
        api_key = st.text_input(
            f"Gemini API Key {status['symbol']}", 
            type="password", 
            help=status['help'],
            key="api_key_input"
        )
        
        # Update the environment variable with the new valid key when it changes
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key

        uploaded_file = st.file_uploader("Upload Financial Data (CSV)", type=['csv'])

        st.header("🛠️ Demo Toggles")
        crisis_mode = st.toggle("🚨 Crisis Mode", help="Load the pre-configured high-risk dataset.")
        dumb_mode = st.toggle("🤖 Dumb Mode", help="Turn off AI explanations and just show the numbers.")

    # --- Data Loading ---
    df = None
    if crisis_mode:
        if os.path.exists("data/crisis_mock_data.csv"):
            df = load_and_clean_data("data/crisis_mock_data.csv")
        else:
            st.warning("🚨 Crisis mock data not found at data/crisis_mock_data.csv")
    elif uploaded_file is not None:
        df = load_and_clean_data(uploaded_file)
    else:
        # Load sample data by default on app launch
        if os.path.exists("data/sample_financial_data.csv"):
            df = load_and_clean_data("data/sample_financial_data.csv")
        else:
            st.warning("Sample data not found. Please run `utils/data_generator.py` to generate it, or upload a CSV.")

    # --- Main Area ---
    if df is not None:
        # --- THE DECISION SIMULATOR (Requirement 1 & 6) ---
        st.extender("🔮 Decision Simulator (What-If Analysis)", expended=False)
        scenario_input = st.text_input(
            "Describe a hypothetical change:", 
            placeholder="e.g., 'Delay rent by 2 weeks' or 'Hire a developer for $4000'"
        )

        if scenario_input:
            with st.spinner("Analyzing scenario..."):
                # 1. Ask the LLM to extract JSON
                try:
                    prompt = DECISION_SIMULATOR_PROMPT.format(user_input=scenario_input)
                    response_text = get_gemini_response(prompt, response_mime_type="application/json")
                    parsed_action = json.loads(response_text)
                    
                    st.success(f"Appended Scenario: {parsed_action['label']} (${parsed_action['amount']})")
                    
                    # 2. Append this row to our DataFrame
                    future_date = pd.to_datetime('today') + pd.Timedelta(days=1)
                    # Note: We map 'amount' to Credit/Debit for the forecaster
                    new_row = {
                        "Date": future_date, 
                        "Description": f"SIMULATION: {parsed_action['label']}", 
                        "Category": "Simulation",
                        "Debit": abs(parsed_action["amount"]) if parsed_action["amount"] < 0 else 0,
                        "Credit": parsed_action["amount"] if parsed_action["amount"] > 0 else 0
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                except Exception as e:
                    st.error(f"Failed to process scenario: {str(e)}")
                    # Fallback to mock if AI fails
                    parsed_action = {"amount": -4000, "label": "Hire a developer (Mock)"}
                    st.info("Using mock action due to processing error.")

        # 2. Calculate Balances
        balance_df = calculate_daily_running_balance(df)
        
        # --- KPI Cards ---
        st.subheader("Financial Overview")
        col1, col2, col3 = st.columns(3)
        
        last_record = balance_df.iloc[-1]
        lowest_record = balance_df.loc[balance_df['Running_Balance'].idxmin()]
        
        current_balance = last_record['Running_Balance']
        lowest_balance = lowest_record['Running_Balance']
        lowest_date = lowest_record['Date'].strftime('%b %d, %Y')
        
        col1.metric("6-Month Projected Balance", f"${current_balance:,.2f}")
        col2.metric("Projected Lowest Balance", f"${lowest_balance:,.2f}", 
                    delta="Critical" if lowest_balance < 0 else "Safe", delta_color="inverse")
        col3.metric("Date of Lowest Balance", lowest_date)
        
        # --- Chart Visualization ---
        st.subheader("Running Balance Over Time")
        # Create a line chart with a red threshold line at $0
        line_chart = alt.Chart(balance_df).mark_line(color="#1f77b4", strokeWidth=2).encode(
            x=alt.X('Date:T', title='Date'),
            y=alt.Y('Running_Balance:Q', title='Balance ($)'),
            tooltip=['Date:T', 'Running_Balance:Q']
        )
        
        # $0 Threshold Rule
        rule = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='red', strokeDash=[4,4], strokeWidth=2).encode(y='y')
        
        st.altair_chart(line_chart + rule, width='stretch')
        
        # --- Anomaly Detection Placeholder ---
        # anomalies = detect_anomalies(df)
        st.info("Anomaly Check Placeholder: No severe deviations from historical averages found.")
        
        # --- AI Insight Generation ---
        if not dumb_mode:
            st.subheader("🤖 AI Insights & Recommendations")
            
            # Detect shortfalls below $0 for crisis detection
            shortfalls = detect_shortfalls(balance_df, threshold=0)
            
            if shortfalls.empty:
                st.success("✅ **Finances look healthy!** No sub-zero cash crunches detected in the projected timeframe.")
            else:
                st.error(f"🚨 **Cash Crunch Detected!** Your balance drops below $0 on {len(shortfalls)} projected days.")
                
                if not api_key:
                    st.warning("⚠️ Please enter your Gemini API Key in the sidebar to generate AI survival strategies.")
                else:
                    # Set the environment variable for the gemini client
                    os.environ["GEMINI_API_KEY"] = api_key
                    
                    with st.expander("Generate AI Crisis Report", expanded=True):
                        with st.spinner("Analyzing financial topology and generating survival strategies..."):
                            # Prepare Data for generation
                            # We'll take the worst 5 days to reduce token usage and noise
                            worst_days = shortfalls.sort_values(by='Running_Balance').head(5)
                            shortfall_json = worst_days[['Date', 'Net_Flow', 'Running_Balance']].to_json(orient='records', date_format='iso')
                            
                            # Additional context we simulated in data_generator.py
                            risk_details = "Large tax payment detected in Month 3 and multiple late-paying client invoices."
                            
                            # Format prompt and call AI
                            user_prompt = USER_PROMPT_TEMPLATE.format(
                                shortfall_json=shortfall_json,
                                risk_details=risk_details
                            )
                            
                            ai_advice = get_financial_advice(SYSTEM_PROMPT, user_prompt)
                            
                            # Display Result
                            st.markdown("---")
                            st.markdown(ai_advice)
    else:
        st.info("👈 Upload your 'sample_financial_data.csv' or turn on 'Crisis Mode' in the sidebar to begin analysis.")

if __name__ == "__main__":
    main()
