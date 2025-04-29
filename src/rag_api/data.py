import os

from langchain_community.document_loaders import (
    Docx2txtLoader,
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader
)
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from src.rag_api.const import (
    DB_DIR,
    EMBEDDINGS_MODEL,
)

embeddings_model = OllamaEmbeddings(model=EMBEDDINGS_MODEL, num_gpu=10, num_thread=10)

db = Chroma(
    persist_directory=DB_DIR,
    embedding_function=embeddings_model,
)

DOC_LOADERS = {
    "pdf": PyPDFLoader, # requires pypdf
    "docx": Docx2txtLoader, # requires docx2txt
    "txt": TextLoader,
    "md": UnstructuredMarkdownLoader, # requires "unstructured[md]" and nltk
}

def is_data_available():
    return True if db.get().get("ids") else False


def store_data(file_path):
    loader = DOC_LOADERS.get(file_path.split(".")[-1].lower())
    if not loader:
        raise ValueError("Unsupported file type")
    doc = loader(file_path).load()
    print("Loading data")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=100,
    )
    chunks = text_splitter.split_documents(doc)
    Chroma.from_documents(documents=chunks, embedding=embeddings_model, persist_directory=DB_DIR)
    print("Done store data")


def remove_file_from_chromadb(file_path):
    """
    Remove all chunks associated with a specific file from ChromaDB
    """
    # Open the database
    db = Chroma(
        persist_directory=DB_DIR,
        embedding_function=embeddings_model,
    )
    
    # Get the current collection
    collection = db.get()
    
    # Find and delete chunks associated with the specific file
    file_to_remove = os.path.basename(file_path)
    
    # Get the current collection
    ids_to_delete = []
    for i, metadata in enumerate(collection['metadatas']):
        # Check if the metadata contains the filename
        if metadata and metadata.get('source', '').endswith(file_to_remove):
            ids_to_delete.append(collection['ids'][i])
    
    # Delete the identified chunks
    if ids_to_delete:
        db._collection.delete(ids=ids_to_delete)
        print(f"Removed {len(ids_to_delete)} chunks associated with {file_to_remove}")
    else:
        print(f"No chunks found for {file_to_remove}")
