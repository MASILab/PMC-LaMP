import streamlit as st

st.write("Now, you have a file containing PMCIDs of papers related to your topic.")
st.write("In this step, we use this file to retrieve the full text articles from PubMed Central in JSON format.")
st.write("To do this, run the fetch_pmc_articles.py script which fetches papers at a rate of ~10k articles/hour.")
