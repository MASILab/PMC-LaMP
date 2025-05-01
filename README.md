# PMC-LaMP: PubMed Central Language Model Pipeline

PMC-LaMP is a tool for creating custom RAG-enabled chatbots based on PubMed Central medical literature. This pipeline allows you to search for scientific articles on a specific topic, download them, create a vector index, and generate a chatbot that can answer questions based on the literature.

## Prerequisites

- Python 3.8+
- Linux/Unix bash environment
- Internet connection
- At least 8GB of RAM
- Disk space proportional to the number of articles (approximately 1GB per 10,000 articles)

### Important Note for Windows Users
This tool requires a bash environment to run. Windows users must use one of the following options:
- Install Windows Subsystem for Linux (WSL) - recommended
- Use a Linux virtual machine
- Use Git Bash (may have limited functionality)

All commands in this README assume a Linux/Unix bash environment.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/PMC-LaMP.git
   cd PMC-LaMP
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables (optional):
   Create a `.env` file in the root directory and add:
   ```
   SERVER_IP=127.0.0.1
   ```

## One-Command Setup and Run (Recommended)

The easiest way to use PMC-LaMP is with our interactive script that guides you through the entire process:

```bash
python simple_pmc_lamp.py
```

This interactive script will:
1. Check your environment and dependencies
2. Ask for your medical topic keyword
3. Guide you through obtaining PMCIDs (or use sample ones)
4. Download the articles
5. Generate the FAISS index
6. Configure the application
7. Start the chatbot servers

You can also provide a topic keyword directly:

```bash
python simple_pmc_lamp.py --keyword cancer
```

The script will walk you through each step and handle all the technical details automatically.

## Starting the Application

If you've already completed the setup (downloading articles and generating the index), you can start the application with:

```bash
chmod +x start_pmc_lamp.sh  # Make the script executable (first time only)
./start_pmc_lamp.sh
```

This script will start the API server and Streamlit interface, opening the web application in your browser.

## Manual Pipeline Workflow

For advanced users who prefer to run each step manually, follow the detailed pipeline below:

### Step 1: Collect PMCIDs for your topic

1. Go to https://pmc.ncbi.nlm.nih.gov/ and search for your topic
2. On the left column, apply filters:
   - Select the 'Open Access' filter under article attributes
   - Optionally, limit the publication date range
3. Export the results:
   - Click 'Send to:' (located under the right side of the search bar)
   - Under 'Choose Destination', select 'File'
   - In the 'Format' dropdown, select 'PMCID List'
   - Click the 'Create File' button to download the file
4. Create a directory called `pmcids` in the project root if it doesn't exist
5. Move the downloaded file to the `pmcids` directory and rename it if desired (format: `keyword_pmc_result.txt`)

### Step 2: Download Articles from PubMed Central

Run the article download script with your PMCID list:

```bash
bash fetch_pmc_articles.sh pmcids/your_keyword_pmc_result.txt
```

This will download BioC JSON formatted articles to `fulltext_articles/your_keyword_pmc_articles/` directory.

### Step 3: Generate FAISS Index

Generate a vector index from the downloaded articles:

```bash
python index_generator.py --document_path fulltext_articles/your_keyword_pmc_articles/ --input_type json
```

Optional parameters:
- `--max_files`: Maximum number of files to process (default: 250000)
- `--group_size`: Number of documents to process per group (default: 1000)
- `--chunk_size`: Size of text chunks for indexing (default: 1000)
- `--chunk_overlap`: Overlap between chunks (default: 20)

The index will be saved to `indexes/faiss_index/`.

### Step 4: Configure the Chatbot

Update the `config.py` file to point to your newly created index:

```python
FAISS_INDEX = "indexes/faiss_index"
```

### Step 5: Start the Chatbot

1. Start the API server:
   ```bash
   python app.py
   ```

2. In a separate terminal, start the Streamlit interface:
   ```bash
   streamlit run PMC-LaMP.py
   ```

3. Navigate to the Chatbot page from the sidebar and start asking questions!

## Advanced Configuration

### Customizing Prompt Templates

The file `prompt_templates.py` contains different templates for various types of queries:
- `question_answering_prompt`: General question answering
- `future_research_prompt`: Suggesting future research directions
- `implications_prompt`: Discussing broader implications
- `comparative_analysis_prompt`: Comparing research findings

You can modify these templates to customize the chatbot's responses.

### Changing Models

In `config.py`, you can change the models used:
- `READER_MODEL`: The LLM used for generating responses
- `EMBEDDING_MODEL`: The model used for text embeddings
- `RERANKER_MODEL`: The model used for reranking search results

## Troubleshooting

- If the article download fails, check your internet connection and try again.
- If you encounter memory issues during index generation, try reducing the `--group_size` parameter.
- If the chatbot doesn't start, check that both the API server and Streamlit interface are running.
- For Windows users, ensure you have properly set up WSL or a Linux VM before attempting to run the application.

## License

[Your license information here]

## Contact

For questions or feedback, please contact: valiant@vanderbilt.edu
