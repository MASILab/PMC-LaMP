#!/usr/bin/env python
import os
import sys
import argparse
import subprocess
import time
from pathlib import Path

def ensure_directory(directory):
    """Create directory if it doesn't exist."""
    Path(directory).mkdir(parents=True, exist_ok=True)
    
def run_command(command, description):
    """Run a command with error handling and user feedback."""
    print(f"\n{'=' * 80}\n{description}\n{'=' * 80}")
    try:
        result = subprocess.run(command, shell=True, check=True, text=True)
        print(f"✓ {description} completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error during {description}. Error code: {e.returncode}")
        print(f"Error details: {e}")
        return False

def download_articles(pmcid_file):
    """Download articles using the fetch_pmc_articles.sh script."""
    if not os.path.exists(pmcid_file):
        print(f"Error: PMCID file '{pmcid_file}' does not exist.")
        return False
    
    return run_command(
        f"bash fetch_pmc_articles.sh {pmcid_file}",
        "Downloading articles from PubMed Central"
    )

def generate_index(articles_dir, max_files=250000, group_size=1000, chunk_size=1000, chunk_overlap=20):
    """Generate FAISS index from downloaded articles."""
    if not os.path.exists(articles_dir):
        print(f"Error: Articles directory '{articles_dir}' does not exist.")
        return False
    
    command = (
        f"python index_generator.py "
        f"--document_path {articles_dir} "
        f"--input_type json "
        f"--max_files {max_files} "
        f"--group_size {group_size} "
        f"--chunk_size {chunk_size} "
        f"--chunk_overlap {chunk_overlap}"
    )
    
    return run_command(command, "Generating FAISS index")

def update_config(index_path):
    """Update the config.py file with the new index path."""
    try:
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
        print(f"✗ Error updating config.py: {e}")
        return False

def start_servers():
    """Start the API server and Streamlit interface."""
    # Start API server in background
    api_process = subprocess.Popen(
        ["python", "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a bit for the API to start
    time.sleep(3)
    
    if api_process.poll() is not None:
        print("✗ API server failed to start.")
        return False
    
    print("✓ API server started successfully.")
    
    # Start Streamlit interface
    streamlit_process = subprocess.Popen(
        ["streamlit", "run", "PMC-LaMP.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a bit for Streamlit to start
    time.sleep(3)
    
    if streamlit_process.poll() is not None:
        print("✗ Streamlit interface failed to start.")
        api_process.terminate()
        return False
    
    print("✓ Streamlit interface started successfully.")
    print("\nThe PMC-LaMP application is now running. Access the Streamlit interface in your browser.")
    print("Press Ctrl+C to stop the servers when done.")
    
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
    parser = argparse.ArgumentParser(description="PMC-LaMP Pipeline Runner")
    parser.add_argument("--step", choices=["all", "download", "index", "config", "run"], default="all",
                       help="Which step of the pipeline to run (default: all)")
    parser.add_argument("--pmcid-file", type=str, help="Path to the PMCID list file")
    parser.add_argument("--articles-dir", type=str, help="Path to the downloaded articles directory")
    parser.add_argument("--index-path", type=str, default="indexes/faiss_index", 
                       help="Path for the FAISS index (default: indexes/faiss_index)")
    parser.add_argument("--max-files", type=int, default=250000, help="Maximum number of files to process")
    parser.add_argument("--group-size", type=int, default=1000, help="Number of documents to process per group")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Size of text chunks for indexing")
    parser.add_argument("--chunk-overlap", type=int, default=20, help="Overlap between chunks")
    
    args = parser.parse_args()
    
    # Create necessary directories
    ensure_directory("pmcids")
    ensure_directory("fulltext_articles")
    ensure_directory("indexes")
    
    if args.step in ["all", "download"]:
        if not args.pmcid_file:
            parser.error("--pmcid-file is required for the download step")
        if not download_articles(args.pmcid_file):
            if args.step == "all":
                print("Download step failed. Stopping pipeline.")
                return
    
    if args.step in ["all", "index"]:
        if args.step == "all" and args.pmcid_file:
            # Extract keyword from filename
            keyword = os.path.basename(args.pmcid_file).split("_")[0]
            articles_dir = f"fulltext_articles/{keyword}_pmc_articles"
        elif not args.articles_dir:
            parser.error("--articles-dir is required for the index step")
        else:
            articles_dir = args.articles_dir
        
        if not generate_index(
            articles_dir, 
            args.max_files, 
            args.group_size, 
            args.chunk_size, 
            args.chunk_overlap
        ):
            if args.step == "all":
                print("Index generation step failed. Stopping pipeline.")
                return
    
    if args.step in ["all", "config"]:
        if not update_config(args.index_path):
            if args.step == "all":
                print("Config update step failed. Stopping pipeline.")
                return
    
    if args.step in ["all", "run"]:
        start_servers()

if __name__ == "__main__":
    main() 