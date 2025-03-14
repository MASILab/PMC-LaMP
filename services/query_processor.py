import time
import logging
from typing import Optional, List, Tuple
from langchain_community.vectorstores import FAISS
from transformers import pipeline
from ragatouille import RAGPretrainedModel
from .utils import format_time

log = logging.getLogger(__name__)


def answer_with_rag(
    question: str,
    llm: pipeline,
    knowledge_index: FAISS,
    prompt_template: str,
    reranker: Optional[RAGPretrainedModel] = None,
    num_retrieved_docs: int = 100,
    num_docs_final: int = 5,
) -> Tuple[str, List[Tuple[str, str, float]]]:
    """Generates an answer to the user queries with references"""
    answer_start_time = time.time()

    log.info("Retrieving documents...")
    docs_with_scores = knowledge_index.similarity_search_with_score(
        query=question, k=num_retrieved_docs
    )

    doc_contents = [doc.page_content for doc, _ in docs_with_scores]
    doc_metadata = [doc.metadata["source"] for doc, _ in docs_with_scores]
    doc_scores = [score for _, score in docs_with_scores]

    if reranker:
        log.info("Reranking documents...")
        reranked_docs = reranker.rerank(question, doc_contents, k=num_docs_final)
        reranked_contents = [
            rdoc["content"] if isinstance(rdoc, dict) else rdoc
            for rdoc in reranked_docs
        ]

        relevant_docs = [
            (
                content,
                doc_metadata[doc_contents.index(content)],
                doc_scores[doc_contents.index(content)],
            )
            for content in reranked_contents
        ]
    else:
        relevant_docs = [
            (doc_contents[i], doc_metadata[i], doc_scores[i])
            for i in range(num_docs_final)
        ]

    context = "\nExtracted documents:\n"
    for i, (content, _, _) in enumerate(relevant_docs):
        context += f"Document {i + 1}:::\n{content}\n"

    final_prompt = prompt_template.format(question=question, context=context)
    log.info("Generating answer...")
    answer = llm(final_prompt)[0]["generated_text"]
    answer_elapsed_time = format_time(time.time() - answer_start_time)
    log.info(f"Answer generated in {answer_elapsed_time}")

    return answer, relevant_docs
