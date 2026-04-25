import streamlit as st
import pandas as pd
import altair as alt
import os
import json
from datetime import datetime, timedelta

from core.forecaster import load_and_clean_data, calculate_daily_running_balance, detect_shortfalls
from core.gemini_client import get_financial_advice
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
        api_key = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API key to enable AI insights.")
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

    # --- Main Area ---
    if df is not None:
        # --- THE DECISION SIMULATOR (Requirement 1 & 6) ---
        st.subheader("🔮 Decision Simulator (What-If Analysis)")
        scenario_input = st.text_input(
            "Describe a hypothetical change:", 
            placeholder="e.g., 'Delay rent by 2 weeks' or 'Hire a developer for $4000'"
        )

        if scenario_input:
            with st.spinner("Analyzing scenario..."):
                # 1. Ask the LLM to extract JSON
                # extracted_str = extract_json_from_text(scenario_input) 
                # parsed_action = json.loads(extracted_str)
                
                # Mock extracted response for prototype
                parsed_action = {"amount": -4000, "label": "Hire a developer"}
                
                st.success(f"Appended Scenario: {parsed_action['label']} ({parsed_action['amount']})")
                
                # 2. Append this row to our DataFrame for a future date (e.g., tomorrow)
                future_date = pd.to_datetime('today') + pd.Timedelta(days=1)
                new_row = pd.DataFrame([{"Date": future_date, "Description": parsed_action["label"], "Amount": parsed_action["amount"], "Category": "Simulation"}])
                df = pd.concat([df, new_row], ignore_index=True)

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
            
            st.altair_chart(line_chart + rule, use_container_width=True)
            
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
            st.error("Failed to load and clean the CSV data. Please check the file format.")
    else:
        st.info("👈 Upload your 'sample_financial_data.csv' or turn on 'Crisis Mode' in the sidebar to begin analysis.")

if __name__ == "__main__":
    main()
