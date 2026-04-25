import os
import google.genai as genai
from google.api_core.exceptions import DeadlineExceeded

def get_financial_advice(system_prompt, user_data_json):
    """
    Calls the Google Gemini API to get financial advice based on a system prompt and user data.
    
    Args:
        system_prompt (str): The persona and instructions for the AI.
        user_data_json (str): The JSON string containing the financial shortfall data.

    Returns:
        str: The Markdown text response from the Gemini API.
    """
    # 1. Setup API Key (The official SDK handles the Content-Type and Authorization headers internally)
    api_key = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
    # api_key = "AIzaSyANUd_SHTHLN3FsOMeTwneac9qDl1-8hvU"
    if not api_key or api_key == "YOUR_GEMINI_API_KEY":
        return "Error: GEMINI_API_KEY environment variable not set."
    
    genai.configure(api_key=api_key)

    try:
        # 2. Use Gemini 1.5 Pro to support System Instructions
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            system_instruction=system_prompt
        )

        # 3. Call the API with the user data and a network timeout
        # request_options allows setting the timeout in seconds for the gRPC/REST call
        response = model.generate_content(
            user_data_json,
            request_options={"timeout": 30.0}
        )

        # 4. Handle JSON internally and return ONLY the text content
        return response.text

    except DeadlineExceeded:
        return "Error: API request timed out. Please check your network connection and try again."
    except Exception as e:
        return f"Error: An unexpected issue occurred during the API call: {str(e)}"

if __name__ == "__main__":
    # Example usage for testing
    sample_system_prompt = "You are a financial crisis advisor."
    sample_user_data = '{"shortfalls": [{"Date": "2026-03-15", "Balance": -2000}]}'
    
    # Needs GEMINI_API_KEY exported in your environment to work
    # print(get_financial_advice(sample_system_prompt, sample_user_data))
