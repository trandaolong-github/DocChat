import requests
import os

from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    Docx2txtLoader,
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader
)
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama

from src.rag_api.const import DB_DIR, DOC_DIR, EMBEDDINGS_MODEL, OLLAMA_HOST, OLLAMA_PORT


class NoModelsAvailableError(Exception):
    """Custom exception for no models available in Ollama"""
    pass


template = """Your job is to use the following context to answer questions.
Be as detailed as possible, but don't make up any information that's not
from the context. If you don't know an answer, say you don't know.
Never answer the questions that doesn't relate to the context.
Below is the context:
{context}
"""

# template = """Your job is to use the persentation of the code base
# to answer all questions about it. Use the following context to answer questions.
# Be as detailed as possible, but don't make up any information that's not from the context.
# If you don't know an answer, say you don't know. Never answer the questions that
# doesn't relate to the context.
# {context}
# """

system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["context"], template=template)
)

human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["question"], template="{question}")
)
messages = [system_prompt, human_prompt]

review_prompt = ChatPromptTemplate(
    input_variables=["context", "question"], messages=messages
)

embeddings_model = OllamaEmbeddings(model=EMBEDDINGS_MODEL, num_gpu=10, num_thread=10)

db = Chroma(
    persist_directory=DB_DIR,
    embedding_function=embeddings_model,
)

retriever = db.as_retriever(search_kwargs={"k": 10})


LLM_QA_MAPPING = dict()

DOC_LOADERS = {
    "pdf": PyPDFLoader, # requires pypdf
    "docx": Docx2txtLoader, # requires docx2txt
    "txt": TextLoader,
    "md": UnstructuredMarkdownLoader, # requires "unstructured[md]" and nltk
}


def is_data_available():
    return True if db.get().get("ids") else False


def remove_file_from_chromadb(file_name):
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
    
    # Get the current collection
    ids_to_delete = []
    for i, metadata in enumerate(collection['metadatas']):
        # Check if the metadata contains the filename
        if metadata and metadata.get('source', '').endswith(file_name):
            ids_to_delete.append(collection['ids'][i])
    
    # Delete the identified chunks
    if ids_to_delete:
        db._collection.delete(ids=ids_to_delete)
        print(f"Removed {len(ids_to_delete)} chunks associated with {file_name}")
        os.remove(os.path.join(DOC_DIR, file_name))
    else:
        print(f"No chunks found for {file_name}")


def get_available_models():
    """Get available models from the Ollama"""
    try:
        resp = requests.get(f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/tags")
        resp.raise_for_status()
        return [
            model["name"]
            for model in resp.json()["models"]
            if model["name"] != EMBEDDINGS_MODEL
        ]
    except requests.exceptions.HTTPError as e:
        raise NoModelsAvailableError(f"Error connecting to Ollama: {e}")
    except Exception as e:
        raise NoModelsAvailableError(f"Error fetching models: {e}")


def get_qa_agent(model_name: str):
    """Get QA agent bases on the Ollama model"""
    try:
        return LLM_QA_MAPPING[model_name]
    except KeyError:
        qa = RetrievalQA.from_chain_type(
            llm=Ollama(model=model_name),
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
        )
        qa.combine_documents_chain.llm_chain.prompt = review_prompt
        LLM_QA_MAPPING[model_name] = qa
        return qa


def store_data(file_name, content):
    loader = DOC_LOADERS.get(file_name.split(".")[-1].lower())
    if not loader:
        raise ValueError("Unsupported file type")
    try:
        file_path = os.path.join(DOC_DIR, file_name)
        with open(file_path, "wb") as f:
            f.write(content.file.read())
    except (IOError, OSError) as e:
        raise Exception(f"Error writing file: {str(e)}")

    try:
        doc = loader(file_path).load()
        print("Loading data")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=100,
        )
        chunks = text_splitter.split_documents(doc)
        Chroma.from_documents(documents=chunks, embedding=embeddings_model, persist_directory=DB_DIR)
        print("Done store data")
    except Exception as e:
        os.remove(file_path)  # Clean up the file if there's an error
        raise Exception(f"Error embedding file: {str(e)}")
