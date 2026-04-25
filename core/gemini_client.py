import os
from google import genai
from google.genai import types

def get_gemini_response(prompt, system_instruction=None, response_mime_type=None):
    """
    Generic helper to get a response from Gemini.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    
    client = genai.Client(api_key=api_key)
    
    config = {}
    if system_instruction:
        config["system_instruction"] = system_instruction
    if response_mime_type:
        config["response_mime_type"] = response_mime_type
    
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=prompt,
        config=config
    )
    return response.text

def get_financial_advice(system_prompt, user_data_json):
    """
    Calls the Google Gemini API to get financial advice based on a system prompt and user data.
    """
    try:
        return get_gemini_response(user_data_json, system_instruction=system_prompt)
    except Exception as e:
        return f"Error: An unexpected issue occurred during the API call: {str(e)}"


if __name__ == "__main__":
    # Example usage for testing
    sample_system_prompt = "You are a financial crisis advisor."
    sample_user_data = '{"shortfalls": [{"Date": "2026-03-15", "Balance": -2000}]}'
    
    # Needs GEMINI_API_KEY exported in your environment to work
    # print(get_financial_advice(sample_system_prompt, sample_user_data))
