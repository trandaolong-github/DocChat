import requests

from langchain.chains import RetrievalQA
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_community.llms import Ollama

from src.rag_api.data import db
from src.rag_api.const import EMBEDDINGS_MODEL, OLLAMA_HOST, OLLAMA_PORT


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

retriever = db.as_retriever(search_kwargs={"k": 10})


LLM_QA_MAPPING = dict()


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
