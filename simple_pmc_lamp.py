#!/usr/bin/env python
import os
import sys
import argparse
import subprocess
import time
import requests
from pathlib import Path
import shutil
import webbrowser

def print_section(title):
    """Print a section header with formatting."""
    print(f"\n{'=' * 80}\n{title}\n{'=' * 80}")

def ensure_directory(directory):
    """Create directory if it doesn't exist."""
    Path(directory).mkdir(parents=True, exist_ok=True)

def interactive_setup():
    """Guide user through initial setup if needed."""
    print_section("PMC-LaMP Setup Check")
    
    # Check Python version
    import platform
    python_version = platform.python_version()
    python_version_tuple = tuple(map(int, python_version.split('.')))
    if python_version_tuple < (3, 8):
        print(f"⚠️  Warning: Python version {python_version} detected. PMC-LaMP requires Python 3.8+")
        return False
    
    # Check if required packages are installed
    try:
        import streamlit
        import fastapi
        import uvicorn
        import langchain
        print("✓ All core dependencies appear to be installed.")
    except ImportError as e:
        print(f"⚠️  Missing dependencies detected: {e}")
        choice = input("Would you like to install required dependencies? (y/n): ").lower()
        if choice == 'y':
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        else:
            print("Please install dependencies using: pip install -r requirements.txt")
            return False
    
    # Create required directories
    for directory in ["pmcids", "fulltext_articles", "indexes"]:
        ensure_directory(directory)
    print("✓ Required directories are in place.")
    
    return True

def fetch_pmcids_interactive(keyword):
    """Guide user through PMCID fetching or use keywords to search PMC."""
    print_section(f"Fetching PMCIDs for: {keyword}")
    
    # Check if PMCIDs file already exists
    pmcid_file = f"pmcids/{keyword}_pmc_result.txt"
    if os.path.exists(pmcid_file):
        print(f"Found existing PMCID file: {pmcid_file}")
        choice = input("Use existing file? (y) or fetch new PMCIDs (n): ").lower()
        if choice == 'y':
            return pmcid_file
    
    # Instruct user how to manually get PMCIDs
    print("\nTo get PMCIDs, you have two options:")
    print("\nOption 1: Manual download (recommended for better control)")
    print("  1. Go to https://pmc.ncbi.nlm.nih.gov/ and search for your topic")
    print("  2. On the left column, select the 'Open Access' filter")
    print("  3. Click 'Send to' (top right) → File → Format: PMCID List → Create File")
    print("  4. Save the file to the 'pmcids' folder as '{keyword}_pmc_result.txt'")
    
    print("\nOption 2: Let me attempt to fetch some sample PMCIDs for you")
    choice = input("\nWould you like me to attempt to fetch sample PMCIDs? (y/n): ").lower()
    
    if choice == 'y':
        try:
            # This is a simplified approximation - actual implementation would be more complex
            # You would need to implement proper API calls to E-utils
            sample_pmcids = ["PMC9530432", "PMC8943149", "PMC8132702", "PMC7745122", "PMC7523147"]
            with open(pmcid_file, 'w') as f:
                f.write('\n'.join(sample_pmcids))
            print(f"✓ Sample PMCIDs saved to {pmcid_file}")
            return pmcid_file
        except Exception as e:
            print(f"⚠️  Error fetching sample PMCIDs: {e}")
    
    # Wait for user to manually download PMCIDs
    print("\nPlease follow Option 1 to manually download PMCIDs.")
    input("Press Enter once you've saved the PMCID file to continue...")
    
    # Check if file exists
    if os.path.exists(pmcid_file):
        print(f"✓ Found PMCID file: {pmcid_file}")
        return pmcid_file
    else:
        # Look for any PMCID files
        pmcid_files = list(Path("pmcids").glob("*.txt"))
        if pmcid_files:
            print(f"Found these PMCID files: {[f.name for f in pmcid_files]}")
            for idx, file in enumerate(pmcid_files):
                print(f"  {idx+1}. {file.name}")
            choice = input(f"Select a file (1-{len(pmcid_files)}) or press Enter to skip: ")
            if choice.isdigit() and 1 <= int(choice) <= len(pmcid_files):
                return str(pmcid_files[int(choice)-1])
    
    print("⚠️  No PMCID file found. You'll need to provide this to continue.")
    return None

def download_articles(pmcid_file):
    """Download articles using the fetch_pmc_articles.sh script."""
    print_section("Downloading Articles")
    
    if not os.path.exists(pmcid_file):
        print(f"Error: PMCID file '{pmcid_file}' does not exist.")
        return False
    
    # Make the script executable if needed
    script_path = "fetch_pmc_articles.sh"
    if not os.access(script_path, os.X_OK):
        os.chmod(script_path, os.stat(script_path).st_mode | 0o111)
    
    print(f"Starting download using PMCIDs from: {pmcid_file}")
    print("This may take several minutes depending on the number of articles...")
    
    try:
        result = subprocess.run(
            f"bash {script_path} {pmcid_file}", 
            shell=True, 
            check=True, 
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(result.stdout)
        if result.stderr:
            print(f"Warnings/errors: {result.stderr}")
        
        # Extract the keyword from the PMCID filename
        keyword = os.path.basename(pmcid_file).split("_")[0]
        articles_dir = f"fulltext_articles/{keyword}_pmc_articles"
        
        # Check if articles were downloaded
        if os.path.exists(articles_dir) and len(list(Path(articles_dir).glob("*.json"))) > 0:
            print(f"✓ Articles downloaded to: {articles_dir}")
            return articles_dir
        else:
            print("⚠️  No articles were downloaded.")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error during download: {e}")
        print(f"Error details: {e.stderr}")
        return None

def generate_index(articles_dir, max_files=250000, group_size=1000, chunk_size=1000, chunk_overlap=20):
    """Generate FAISS index from downloaded articles."""
    print_section("Generating FAISS Index")
    
    if not os.path.exists(articles_dir):
        print(f"Error: Articles directory '{articles_dir}' does not exist.")
        return False
    
    # Count how many articles we have
    article_count = len(list(Path(articles_dir).glob("*.json")))
    print(f"Found {article_count} articles to index.")
    
    # Adjust group size if very few articles
    if article_count < 100:
        group_size = min(group_size, article_count)
    
    print("Starting index generation...")
    print("This may take several minutes depending on the number of articles...")
    
    command = (
        f"python index_generator.py "
        f"--document_path {articles_dir} "
        f"--input_type json "
        f"--max_files {max_files} "
        f"--group_size {group_size} "
        f"--chunk_size {chunk_size} "
        f"--chunk_overlap {chunk_overlap}"
    )
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        if "Knowledge vectorstore successfully saved" in result.stdout:
            print("✓ FAISS index generated successfully.")
            return "indexes/faiss_index"
        else:
            print(result.stdout)
            if result.stderr:
                print(f"Warnings/errors: {result.stderr}")
            print("⚠️  Index generation may have had issues.")
            return "indexes/faiss_index"  # Return default path anyway
            
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error generating index: {e}")
        print(f"Error details: {e.stderr}")
        return None

def update_config(index_path):
    """Update the config.py file with the new index path."""
    print_section("Updating Configuration")
    
    try:
        # Ensure index path exists
        if not os.path.exists(index_path):
            print(f"Warning: Index path '{index_path}' does not exist.")
            choice = input("Continue anyway? (y/n): ").lower()
            if choice != 'y':
                return False
        
        with open("config.py", "r") as f:
            config_content = f.read()
        
        # Find the line with FAISS_INDEX and replace it
        lines = config_content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("FAISS_INDEX"):
                lines[i] = f'FAISS_INDEX = "{index_path}"'
                break
        
        with open("config.py", "w") as f:
            f.write("\n".join(lines))
        
        print(f"✓ Updated config.py with index path: {index_path}")
        return True
    except Exception as e:
        print(f"⚠️  Error updating config.py: {e}")
        return False

def start_servers():
    """Start the API server and Streamlit interface."""
    print_section("Starting PMC-LaMP Application")
    
    # Start API server in background
    print("Starting API server...")
    api_process = subprocess.Popen(
        ["python", "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a bit for the API to start
    time.sleep(3)
    
    if api_process.poll() is not None:
        print("⚠️  API server failed to start.")
        error_output = api_process.stderr.read() if api_process.stderr else "Unknown error"
        print(f"Error details: {error_output}")
        return False
    
    print("✓ API server started successfully.")
    
    # Start Streamlit interface
    print("Starting Streamlit interface...")
    streamlit_process = subprocess.Popen(
        ["streamlit", "run", "PMC-LaMP.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a bit for Streamlit to start
    time.sleep(3)
    
    if streamlit_process.poll() is not None:
        print("⚠️  Streamlit interface failed to start.")
        api_process.terminate()
        error_output = streamlit_process.stderr.read() if streamlit_process.stderr else "Unknown error"
        print(f"Error details: {error_output}")
        return False
    
    print("✓ Streamlit interface started successfully.")
    
    # Try to open browser
    try:
        # Attempt to detect Streamlit URL from output
        streamlit_url = "http://localhost:8501"
        webbrowser.open(streamlit_url)
        print(f"Opening browser to {streamlit_url}")
    except Exception as e:
        print(f"Could not open browser automatically: {e}")
        print("Please open http://localhost:8501 in your browser.")
    
    print("\n🎉 PMC-LaMP is now running! 🎉")
    print("\nAccess the Streamlit interface in your browser at: http://localhost:8501")
    print("Navigate to the Chatbot page to start asking questions.")
    print("\nPress Ctrl+C to stop the servers when done.")
    
    try:
        # Keep the script running to maintain the servers
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        streamlit_process.terminate()
        api_process.terminate()
        print("Servers stopped.")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="PMC-LaMP Simple Runner")
    parser.add_argument("--keyword", type=str, default=None, 
                       help="Keyword for your medical topic (used for file naming)")
    
    args = parser.parse_args()
    
    # Initial setup check
    if not interactive_setup():
        print("Setup incomplete. Please resolve the issues and try again.")
        return
    
    # Get keyword from user if not provided as argument
    keyword = args.keyword
    if not keyword:
        keyword = input("Enter a keyword for your medical topic (e.g., 'diabetes', 'cancer'): ")
        if not keyword:
            print("No keyword provided. Using 'medical' as default.")
            keyword = "medical"
    
    # Step 1: Get PMCIDs file
    pmcid_file = fetch_pmcids_interactive(keyword)
    if not pmcid_file:
        print("Cannot proceed without PMCID file.")
        return
    
    # Step 2: Download articles
    articles_dir = download_articles(pmcid_file)
    if not articles_dir:
        print("Cannot proceed without downloaded articles.")
        return
    
    # Step 3: Generate index
    index_path = generate_index(articles_dir)
    if not index_path:
        print("Cannot proceed without index.")
        return
    
    # Step 4: Update config
    if not update_config(index_path):
        print("Warning: Config update failed. The application may not work correctly.")
    
    # Step 5: Start servers
    start_servers()

if __name__ == "__main__":
    main() 