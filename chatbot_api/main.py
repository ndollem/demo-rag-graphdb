from fastapi import FastAPI
from chatbot_api.rag_agents.doc_rag_agent import doc_rag_agent_executor
from chatbot_api.models.doc_rag_query import DocsQueryInput, DocsQueryOutput
from chatbot_api.utils.async_utils import async_retry

app = FastAPI(
    title="Docs Chatbot",
    description="Endpoints for a document system graph RAG chatbot",
)

@async_retry(max_retries=10, delay=1)
async def invoke_agent_with_retry(query: str):
    """Retry the agent if a tool fails to run.

    This can help when there are intermittent connection issues
    to external APIs.
    """
    return await doc_rag_agent_executor.ainvoke({"input": query})

@app.get("/")
async def get_status():
    return {"status": "running"}

@app.post("/doc-rag-agent")
async def query_doc_agent(query: DocsQueryInput) -> DocsQueryOutput:
    query_response = await invoke_agent_with_retry(query.text)
    query_response["intermediate_steps"] = [
        str(s) for s in query_response["intermediate_steps"]
    ]

    return query_response