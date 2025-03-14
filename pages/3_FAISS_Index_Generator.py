import subprocess
import streamlit as st


def main():
    """
    Provides a file uploader for selecting an input folder.

    If the "Generate FAISS index" button is clicked, the index_generator.py script is run with the selected folder as an argument.
    """
    st.title("FAISS Index Generator")

    uploaded_folder = st.file_uploader(
        "Choose an input folder", accept_multiple_files=True
    )

    if uploaded_folder is not None:
        input_folder_path = f"../{uploaded_folder}"

        if st.button("Generate FAISS Index"):
            try:
                result = subprocess.run(
                    ["python", "index_generator.py", input_folder_path],
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
