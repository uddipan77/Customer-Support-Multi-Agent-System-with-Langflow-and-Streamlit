import requests
import streamlit as st
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

# DataStax Langflow Configuration
BASE_API_URL = "https://aws-us-east-2.langflow.datastax.com"
LANGFLOW_ID = "a8f7cb93-641b-4f79-ae41-568df2d1f4ec" # Replace with your Langflow ID
FLOW_ID = "52e18a16-b47b-41c3-8788-2aa91b80ae2f" # Replace with your Flow ID
ORG_ID = "daaa1ec4-6369-41c3-8175-7588abb4faf6" # Replace with your Organization ID 
APPLICATION_TOKEN = os.environ.get("APP_TOKEN")

def run_flow(message: str) -> dict:
    """Run the Langflow flow with the given message"""
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{FLOW_ID}"
    
    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
        "session_id": str(uuid.uuid4())  # Generate unique session ID
    }
    
    headers = {
        "X-DataStax-Current-Org": ORG_ID,
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    response = requests.post(api_url, json=payload, headers=headers)
    response.raise_for_status()  # Raise exception for bad status codes
    return response.json()

def main():
    st.title("Customer Support Chat")
    
    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about an order (e.g., 'can you lookup order #1001')"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = run_flow(prompt)
                    
                    # Extract the response text from the flow output
                    bot_response = response["outputs"][0]["outputs"][0]["results"]["message"]["text"]
                    st.markdown(bot_response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()
