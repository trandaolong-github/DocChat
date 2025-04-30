import os

from fastapi import FastAPI, HTTPException, UploadFile, File

from src.rag_api.const import DOC_DIR
from src.rag_api.data import is_data_available, store_data, remove_file_from_chromadb
from src.rag_api.rag_core import get_available_models, get_qa_agent
from src.rag_api.models import DataInput, DataOutput, ModelOutput, QueryInput, QueryOutput


app = FastAPI()


@app.get("/available_models")
async def get_models() -> ModelOutput:
    """Get list of available AI models"""
    return {"models": get_available_models()}


@app.get("/uploaded_files")
async def get_uploaded_files() -> list[str]:
    """Get list of uploaded files"""
    return [
        f for f in os.listdir(DOC_DIR)
        if os.path.isfile(os.path.join(DOC_DIR, f)) and not f.startswith('.')
    ]


@app.get("/")
async def root():
    return {"message": "Hello World"}


async def invoke_agent(query: str, llm: str):
    qa = get_qa_agent(llm)
    return await qa.ainvoke(query)


@app.post("/ingest_data")
async def ingest_data(file_name: str, content: UploadFile = File(...)) -> DataOutput:
    print("Ingesting data")
    try:
        store_data(file_name, content)
        #print(f"File {file_name} ingest info: {content}")
        return {"message": "Data stored successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing data: {str(e)}")


@app.post("/remove_data")
async def remove_data(file_name: DataInput) -> DataOutput:
    print("Removing data")
    try:
        remove_file_from_chromadb(file_name.file_name)
        return {"message": "Data was deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting data: {str(e)}")


@app.post("/agent")
async def ask_agent(query: QueryInput) -> QueryOutput:
    if not is_data_available():
        raise HTTPException(status_code=404, detail="Data not available")
    print(f"Processing query: {query.query}, llm: {query.llm}")
    query_response = await invoke_agent(query.query, query.llm)
    sources = set()
    for source in query_response["source_documents"]:
        sources.add(source.metadata["source"].split("/")[-1])
    return {
        "result": query_response["result"],
        "sources": list(sources),
    }
