from fastapi import APIRouter, HTTPException, Request
from schemas import QueryRequest, AnswerResponse, ErrorResponse
from services.query_processor import answer_with_rag

router = APIRouter()


@router.post(
    "/query", response_model=AnswerResponse, responses={400: {"model": ErrorResponse}}
)
async def query(request: QueryRequest, req: Request):
    model_dependencies = req.app.state.model_dependencies

    try:
        answer, relevant_docs_with_source = answer_with_rag(
            question=request.query,
            llm=model_dependencies.reader_llm,
            knowledge_index=model_dependencies.knowledge_base,
            prompt_template=model_dependencies.rag_prompt_template,
            # reranker=model_dependencies.reranker,
        )
        return AnswerResponse(
            query=request.query, answer=answer, references=relevant_docs_with_source
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred while processing the query: {e}"
        )
