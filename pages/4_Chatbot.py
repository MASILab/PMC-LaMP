import os
import sys
import json
import time
import requests
import subprocess
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SERVER_IP = os.getenv("SERVER_IP")


# def start_uvicorn():
#     try:
#         subprocess.run([f"{sys.executable}", "app.py"])

#         with st.spinner("Loading..."):
#             result = subprocess.run([f"{sys.executable}", "app.py"], check=True)
#         if result.returncode == 0:
#             st.success("Uvicorn server started successfully!")
#             st.write(
#                 "The Uvicorn server is now running. If things aren't working, check the terminal where PMC-LaMP.py was started"
#             )
#     except subprocess.CalledProcessError as e:
#         st.error(f"Error starting Uvicorn server: {str(e)}")
#     except Exception as e:
#         st.error(f"Error starting Uvicorn server: {str(e)}")

def start_uvicorn():
    try:
        # Start the subprocess in a separate thread
        subprocess.Popen([f"{sys.executable}", "app.py"])

        # Show the loading bar
        with st.empty():
            with st.progress(0):
                for i in range(100):
                    time.sleep(1)  # Simulate a short loading process
                    st.progress(i + 1)

        # Wait for the subprocess to finish
        result = subprocess.run([f"{sys.executable}", "app.py"], check=True)
        if result.returncode == 0:
            st.success("Uvicorn server started successfully!")
            st.write(
                "The Uvicorn server is now running. If things aren't working, check the terminal where PMC-LaMP.py was started"
            )
    except subprocess.CalledProcessError as e:
        st.error(f"Error starting Uvicorn server: {str(e)}")
    except Exception as e:
        st.error(f"Error starting Uvicorn server: {str(e)}")


def check_server_status():
    try:
        response = requests.get(f"http://{SERVER_IP}:8000")
        return response.status_code == 200
    except requests.ConnectionError:
        return False


def save_conversation(query, response):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.json"
    data = {"timestamp": timestamp, "response": response}
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def send_query_to_server(query):
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
    st.write(f"Response: {answer}")
    st.write("Sources:")

    for i, ref in enumerate(references, start=1):
        content, source, score = ref

        source_link = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{source.split('/')[-1].split('-')[0].strip()}/"
        st.write(
            f"Document {i}: [{source.split('/')[-1].split('-')[0].strip()}]({source_link}) Score: {score:.5f}"
        )


def main():
    st.subheader("Click the button below to start the inference server!")
    if check_server_status():
        st.info("Uvicorn server is already running.")
    else:
        if st.button("Start Uvicorn Server"):
            start_uvicorn()

    st.title("chatbot demo")
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
