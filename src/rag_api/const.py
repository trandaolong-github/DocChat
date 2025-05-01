import os


EMBEDDINGS_MODEL = "mxbai-embed-large:latest"
DB_DIR = "./database"
DOC_DIR = "./uploaded_docs"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", 11434)
