# PMC-LaMP

1) Download a list of PMCIDs based off keyword search on PMC
    - You can download a list of PMCIDs based on keyword search on the website directly.
    - Can be optimized, not yet a priority
2) Utilize BioC API to download relevant paper.
    - Using fetch_pmc_articles.sh
3) Generate a FAISS Index from downloaded articles
4) Create a custom RAG enabled chatbot with scientifically backed responses.
5) Allow interaction with chatbot through both CLI and GUI.
