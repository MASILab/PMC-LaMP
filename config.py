from colbert import Trainer as RAGPretrainedModel

FAISS_INDEX = "indexes/faiss_index"


READER_MODEL = "HuggingFaceH4/zephyr-7b-beta"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L12-v2"
RERANKER_MODEL = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
PROMPT_TEMPLATE = [
    {
        "role": "system",
        "content": """Using the information contained in the context,
        give a comprehensive answer to the question.
        Respond only to the question asked, response should be
        concise and relevant to the question.
        Answer in terms the average person with no technical
        background can easily understand.
        Provide the number of the source document when relevant.
        If the answer cannot be deduced from the context,
        tell the user that there is nothing within the context
        that can be used to answer the question.""",
    },
    {
        "role": "user",
        "content": """Context
        {context}
        ---
        Now here is the question you need to answer.

        Question: {question}""",
    },
]
