import streamlit as st
import subprocess


def main():
    """
    Provides a file uploader for selecting a .txt input file of PMCIDs.

    If the "Begin Downloading" button is clicked, the fetch_pmc_articles.sh script is run with the selected file as an argument.
    """
    st.title("BioC JSON Article Downloader")

    uploaded_file = st.file_uploader("Choose an input file", type="txt")
    if uploaded_file is not None:
        input_file_path = f"pmcids/{uploaded_file.name}"

        if st.button("Begin Downloading"):
            try:
                result = subprocess.run(
                    ["bash", "fetch_pmc_articles.sh", input_file_path],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    st.write(result.stdout)
                else:
                    st.error(
                        f"An error occurred while processing the file: {result.stderr}"
                    )
            except Exception as e:
                st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
