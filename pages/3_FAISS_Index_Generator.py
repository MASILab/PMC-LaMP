import streamlit as st
import time

st.write("Next step is to create a FAISS index from these articles.")
st.write("In order to do this, run the index_generator.py script.")
st.write("This will generate the file necessary to enable RAG for the chatbot.")

st.text_input("index generator")