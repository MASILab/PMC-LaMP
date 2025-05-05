import os
import json
import requests
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
SERVER_IP = os.getenv("SERVER_IP")

def check_server_status():
    """
    Checks the status of the uvicorn server.

    Return:
        bool: True if the server is running and accessible, False otherwise.
    """
    try:
        response = requests.get(f"http://{SERVER_IP}:8000")
        return response.status_code == 200
    except requests.ConnectionError:
        return False


def save_conversation(query, response):
    """
    Saves the query/response pair to a JSON file.

    Args:
        query (str): The user's query.
        response (dict): The response from the language model server.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.json"
    data = {"timestamp": timestamp, "response": response}
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def send_query_to_server(query):
    """
    Sends a query to the uvicorn server and process response.

    Args:
        query (str): The user's query.

    Returns:
        dict: The server's response as a JSON object, or None if an error occurred.
    """
    try:
        url = f"http://{SERVER_IP}:8000/query"
        json_payload = {"query": query}
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=json_payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()

        save_conversation(query, response_data)

        return response.json()
    except Exception as e:
        st.error(f"Error during the query request: {e}")
        return None


def display_conversation(answer, references):
    """
    Displays the conversation response and reference sources.

    Args:
        answer (str): The answer to the user's query.
        references (list): A list of reference tuples (content, source, score).
    """
    st.write(f"Response: {answer}")
    st.write("Sources:")

    for i, ref in enumerate(references, start=1):
        content, source, score = ref

        source_link = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{source.split('/')[-1].split('-')[0].strip()}/"
        st.write(
            f"Document {i}: [{source.split('/')[-1].split('-')[0].strip()}]({source_link}) Score: {score:.5f}"
        )


def main():
    """
    Sets up the Streamlit interface and handles user interactions.
    """
    st.set_page_config(page_title="PMC-LaMP", page_icon="💡")

    col1, col2 = st.columns(2)
    with col1:
        st.image("assets/masi-logo.png")
    with col2:
        st.image("assets/valiant-logo.png")
        st.image("assets/vuse-logo.png")

    st.title("PMC-LaMP Chat Demo")
    st.write(
        "Note: This is a basic demo and accepts only standalone queries at this time"
    )
    st.write(
        "If you have any questions or feedback please reach out to: valiant@vanderbilt.edu"
    )

    query = st.text_input("Enter your query here...", key="query_input")
    submit_button = st.button("Submit Query")

    if submit_button or (query and query != st.session_state.get("last_query")):
        if query:
            st.session_state["last_query"] = query
            with st.spinner("Processing..."):
                response = send_query_to_server(query)

                if response:
                    query = response.get("query", "")
                    answer = response.get("answer", "")
                    references = response.get("references", [])

                    display_conversation(answer, references)
                else:
                    st.error("No response received from the server.")
        else:
            st.warning("Please enter a query.")


if __name__ == "__main__":
    main()
