#!/usr/bin/env python
import os
import sys
import argparse
import subprocess
import time
from pathlib import Path
import importlib.util


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
    python_version_tuple = tuple(map(int, python_version.split(".")))
    if python_version_tuple < (3, 8):
        print(
            f"⚠️  Warning: Python version {python_version} detected. PMC-LaMP requires Python 3.8+"
        )
        return False

    # Check if required packages are installed
    missing_dependencies = []
    for package in ["streamlit", "fastapi", "uvicorn", "langchain"]:
        if importlib.util.find_spec(package) is None:
            missing_dependencies.append(package)

    if missing_dependencies:
        print(f"⚠️  Missing dependencies detected: {', '.join(missing_dependencies)}")
        choice = input(
            "Would you like to install required dependencies? (y/n): "
        ).lower()
        if choice == "y":
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
            )
        else:
            print("Please install dependencies using: pip install -r requirements.txt")
            return False
    else:
        print("✓ All core dependencies appear to be installed.")

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
        if choice == "y":
            return pmcid_file

    # Instruct user how to manually get PMCIDs
    print("\nTo get PMCIDs:")
    print("  1. Go to https://pmc.ncbi.nlm.nih.gov/ and search for your topic")
    print("  2. On the left column, select the 'Open Access' filter")
    print("  3. Click 'Send to' (top right) → File → Format: PMCID List → Create File")
    print("  4. Save the file to the 'pmcids' folder as '{keyword}_pmc_result.txt'")

    # Wait for user to manually download PMCIDs
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
                print(f"  {idx + 1}. {file.name}")
            choice = input(
                f"Select a file (1-{len(pmcid_files)}) or press Enter to skip: "
            )
            if choice.isdigit() and 1 <= int(choice) <= len(pmcid_files):
                return str(pmcid_files[int(choice) - 1])

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

    # Count total PMCIDs to download
    try:
        with open(pmcid_file, "r") as f:
            total_pmcids = len(f.readlines())
        print(f"Found {total_pmcids} PMCIDs to download")
    except Exception as e:
        print(f"Could not count PMCIDs: {e}")
        total_pmcids = 0

    print(f"Starting download using PMCIDs from: {pmcid_file}")
    print("This may take a while depending on the number of articles...")

    # Extract the keyword from the PMCID filename
    keyword = os.path.basename(pmcid_file).split("_")[0]
    articles_dir = f"fulltext_articles/{keyword}_pmc_articles"

    # Setup progress counter
    downloaded = 0
    failed = 0

    # Use Popen to get real-time output
    try:
        process = subprocess.Popen(
            f"bash {script_path} {pmcid_file}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Process output in real-time
        for line in process.stdout:
            # Check if the line contains a download status update
            if "Successfully fetched article" in line:
                downloaded += 1
                pmcid = line.split("article")[1].strip()
                progress = (
                    (downloaded + failed) / total_pmcids * 100
                    if total_pmcids > 0
                    else 0
                )
                print(
                    f"\r[{downloaded}/{total_pmcids}] Downloaded: {progress:.1f}% - Latest: {pmcid}",
                    end="",
                )
            elif "Failed to fetch article" in line:
                failed += 1
                pmcid = line.split("article")[1].split(":")[0].strip()
                print(f"\nFailed to download article: {pmcid}")
            elif "Completed fetching" in line:
                print(f"\n\n{line.strip()}")

        # Wait for process to complete
        process.wait()

        if process.returncode != 0:
            print(f"\n⚠️  Download process exited with code {process.returncode}")
            for line in process.stderr:
                print(f"Error: {line.strip()}")
        else:
            print(
                f"\n✓ Download completed: {downloaded} articles downloaded, {failed} failed"
            )

        # Check if articles were downloaded
        if (
            os.path.exists(articles_dir)
            and len(list(Path(articles_dir).glob("*.json"))) > 0
        ):
            print(f"✓ Articles saved to: {articles_dir}")
            return articles_dir
        else:
            print("⚠️  No articles were downloaded.")
            return None

    except Exception as e:
        print(f"\n⚠️  Error during download: {e}")
        return None


def generate_index(
    articles_dir, keyword, max_files=250000, group_size=1000, chunk_size=1000, chunk_overlap=20
):
    """Generate FAISS index from downloaded articles."""
    print_section("Generating FAISS Index")

    if not os.path.exists(articles_dir):
        print(f"Error: Articles directory '{articles_dir}' does not exist.")
        return False

    # Count how many articles we have
    article_files = list(Path(articles_dir).glob("*.json"))
    article_count = len(article_files)
    print(f"Found {article_count} articles to index.")

    # Adjust group size if very few articles
    if article_count < 100:
        group_size = min(group_size, article_count)
        print(f"Adjusting group size to {group_size} for small article collection")

    # Calculate expected processing groups
    expected_groups = (article_count + group_size - 1) // group_size
    print(f"Will process articles in approximately {expected_groups} groups")

    print("\nStarting index generation...")
    print("This may take a while depending on the number of articles.")
    print("Progress will be displayed as groups are processed:")

    index_name = f"faiss_index_{keyword.replace(' ', '_')}"
    command = (
        f"python3 index_generator.py "
        f"--document_path {articles_dir} "
        f"--input_type json "
        f"--max_files {max_files} "
        f"--group_size {group_size} "
        f"--chunk_size {chunk_size} "
        f"--chunk_overlap {chunk_overlap} "
        f"--index_name {index_name}"
    )

    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Track processing progress
        current_group = 0
        current_file = 0
        articles_processed = 0

        # Process output in real-time
        for line in process.stdout:
            # Look for progress indicators in the output
            if "Processing group" in line and "of files" in line:
                try:
                    # Try to extract the group number
                    current_group = int(
                        line.split("Processing group")[1].split("of")[0].strip()
                    )
                    group_total = expected_groups
                    group_progress = (
                        current_group / group_total * 100 if group_total > 0 else 0
                    )
                    print(
                        f"\r[Group {current_group}/{group_total}] Overall progress: {group_progress:.1f}%",
                        end="",
                    )
                except Exception:
                    print(f"\r{line.strip()}", end="")

            elif "Processing file" in line:
                try:
                    # Extract current file info if possible
                    current_file += 1
                    articles_processed += 1
                    file_progress = (
                        articles_processed / article_count * 100
                        if article_count > 0
                        else 0
                    )

                    # Only update occasionally to avoid too many updates
                    if articles_processed % 10 == 0:
                        print(
                            f"\r[Group {current_group}] Files processed: {articles_processed}/{article_count} ({file_progress:.1f}%)",
                            end="",
                        )
                except Exception:
                    pass

            # Important milestone messages get their own lines
            elif "Converting documents to" in line or "Creating embeddings" in line:
                print(f"\n{line.strip()}")
            elif "Knowledge vectorstore successfully saved" in line:
                print(f"\n\n✅ {line.strip()}")

        # Wait for process to complete
        process.wait()

        # Get any error output
        error_output = process.stderr.read() if process.stderr else ""

        if process.returncode != 0:
            print(f"\n\n⚠️  Index generation exited with code {process.returncode}")
            print(f"Error details: {error_output}")
            return None

        print(
            f"\n✓ Index generation complete! Processed {articles_processed} articles."
        )
        if (
            "Knowledge vectorstore successfully saved"
            in error_output + process.stdout.read()
        ):
            print("✓ FAISS index generated successfully.")
            return f"indexes/{index_name}"
        else:
            print(
                "⚠️  Index generation may have had issues, but appears to have completed."
            )
            return f"indexes/{index_name}"  # Return default path anyway

    except Exception as e:
        print(f"\n⚠️  Error generating index: {e}")
        return None


def update_config(index_path):
    """Update the config.py file with the new index path."""
    print_section("Updating Configuration")

    try:
        # Ensure index path exists
        if not os.path.exists(index_path):
            print(f"Warning: Index path '{index_path}' does not exist.")
            choice = input("Continue anyway? (y/n): ").lower()
            if choice != "y":
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


import platform

def start_servers():
    """Start the API server in a new terminal and Streamlit interface."""
    print_section("Starting PMC-LaMP Application")

    # Start API server in a new terminal window
    print("Starting API server in a new terminal...")
    if platform.system() == "Linux":
        os.system(f"gnome-terminal -- bash -c 'python app.py; exec bash'")
    elif platform.system() == "Darwin":  # macOS
        os.system(f"open -a Terminal 'python app.py'")
    elif platform.system() == "Windows":
        os.system(f"start cmd /k python app.py")
    else:
        print("Unsupported OS for opening a new terminal.")
        return False

    # Wait for the API server to start
    print("Waiting for API server to start...")
    time.sleep(5)  # Adjust this delay if needed

    # Start Streamlit interface
    print("Starting Streamlit interface...")
    streamlit_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "PMC-LaMP.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Wait a bit for Streamlit to start
    time.sleep(3)

    if streamlit_process.poll() is not None:
        print("⚠️  Streamlit interface failed to start.")
        error_output = (
            streamlit_process.stderr.read()
            if streamlit_process.stderr
            else "Unknown error"
        )
        print(f"Error details: {error_output}")
        return False

    print("✓ Streamlit interface started successfully.")

    # Try to open browser
    time.sleep(3)  # Wait a bit for Streamlit to be ready
    try:
        # Attempt to detect Streamlit URL from output
        streamlit_url = "http://localhost:8501"
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
        print("Servers stopped.")

    return True


def prompt_for_existing_index():
    """Prompt the user to select an existing index from the indexes directory."""
    print_section("Select Existing Index")

    index_dir = Path("indexes")
    available_indexes = [d for d in index_dir.iterdir() if d.is_dir() and any(d.iterdir())]

    if available_indexes:
        print("The following indexes are available:")
        for i, index in enumerate(available_indexes, start=1):
            print(f"  {i}. {index.name}")

        choice = input("Enter the number of the index you want to use, or press Enter to skip: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(available_indexes):
            selected_index = available_indexes[int(choice) - 1]
            print(f"✓ Using selected index: {selected_index}")
            return str(selected_index)

    print("No valid index selected or available.")
    return None

# Update the main function to include the prompt for existing index
def main():
    parser = argparse.ArgumentParser(description="PMC-LaMP Simple Runner")
    parser.add_argument(
        "--keyword",
        type=str,
        default=None,
        help="Keyword for your medical topic (used for file naming)",
    )

    args = parser.parse_args()

    # Initial setup check
    if not interactive_setup():
        print("Setup incomplete. Please resolve the issues and try again.")
        return

    # Prompt for existing index
    index_path = prompt_for_existing_index()
    if index_path:
        # Skip the pipeline if an index is already available
        if not update_config(index_path):
            print("Warning: Config update failed. The application may not work correctly.")
        start_servers()
        return

    # Get keyword from user if not provided as argument
    keyword = args.keyword
    if not keyword:
        keyword = input(
            "Enter a keyword for your medical topic (e.g., 'crohn's disease', 'diabetes'): "
        )
        if not keyword:
            print('No keyword provided. Using "crohn\'s disease" as default.')
            keyword = "crohn's disease"

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
    index_path = generate_index(articles_dir, keyword)
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
