from fastapi import FastAPI, HTTPException

from src.rag_api.data import is_data_available, store_data, remove_file_from_chromadb
from src.rag_api.rag_core import qa
from src.rag_api.models import DataInput, DataOutput, QueryInput, QueryOutput

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

async def invoke_agent(query: str):
    return await qa.ainvoke(query)

@app.post("/ingest_data")
async def ingest_data(file_path: DataInput) -> DataOutput:
    print("Ingesting data")
    try:
        store_data(file_path.file_path)
        return {"message": "Data stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing data: {str(e)}")
    
@app.post("/remove_data")
async def remove_data(file_path: DataInput) -> DataOutput:
    print("Removing data")
    try:
        remove_file_from_chromadb(file_path.file_path)
        return {"message": "Data was deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting data: {str(e)}")

@app.post("/agent")
async def ask_agent(query: QueryInput) -> QueryOutput:
    if not is_data_available():
        raise HTTPException(status_code=404, detail="Data not available")
        
    query_response = await invoke_agent(query.text)
    sources = set()
    for source in query_response["source_documents"]:
        sources.add(source.metadata["source"].split("/")[-1])
    return {
        "result": query_response["result"],
        "sources": list(sources),
    }
