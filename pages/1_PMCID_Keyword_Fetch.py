import streamlit as st


def main():
    st.title("PMCID Extraction")

    st.write("1. Go to https://pmc.ncbi.nlm.nih.gov/ and search for your topic")

    st.write("2. On the leftmost column of the website, select:")
    st.markdown("- The 'Open Access' filter under article attributes")
    st.markdown("- Optionally, limit how old the articles are under 'Publication Date'")

    st.write(
        "3. Export the results by clicking 'Send to:' (located under the right side of the search bar)"
    )
    st.markdown("- Under 'Choose Destination', select 'File'")
    st.markdown("- In the 'Format' dropdown, select 'PMCID List'")
    st.markdown("- Click the 'Create File' button to download the file")
    st.write(
        "4. Move the downloaded file to the root directory of your project and rename (especially if you will create multiple chatbots)"
    )

    st.image("assets/PMC Search Screenshot.png")

    st.write("Proceed to the next step.")

    st.markdown(
        """
    <style>
    [data-testid="stMarkdownContainer"] ul{
        list-style-position: inside;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
