# PMC-LaMP

## Pipeline Overview

This repo offers a GUI that will, step by step, go through the pipeline from keyword search to custom RAG-enabled PMC chatbot.

1) Download a list of PMCIDs based off keyword search on PMC
    - You can download a list of PMCIDs based on keyword search on the website directly.
2) Utilize BioC API to download relevant paper.
    - Using fetch_pmc_articles.sh
    - Every 10,000 articles takes up ~1 GB of storage
3) Generate a FAISS Index from downloaded articles
    - Loss is ~1% of the jsons (currently investigating why)
4) Create a custom local RAG enabled chatbot with scientifically backed responses.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Start the web app with the following command:

```bash
streamlit run PMC-LaMP.py
```

Follow the instructions on each page, in order to get a working chatbot.

Make sure to set the correct index for the chatbot in config.py:

```bash
FAISS_INDEX = "indexes/MASI_PDFs_index"
```
