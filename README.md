# PMC-LaMP

1) Download a list of PMCIDs based off keyword search on PMC
    - You can download a list of PMCIDs based on keyword search on the website directly.
    - Can be optimized, not yet a priority
2) Utilize BioC API to download relevant paper.
    - Using fetch_pmc_articles.sh
    - Every 10,000 articles takes up ~1 GB of storage
3) Generate a FAISS Index from downloaded articles
    - Loss is ~1% of the jsons (currently investigating why)
4) Create a custom RAG enabled chatbot with scientifically backed responses.
