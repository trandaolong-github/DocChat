from langchain.chains import RetrievalQA
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_community.llms import Ollama

from src.rag_api.const import LLM_CHAT_MODEL
from src.rag_api.data import db


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
llm = Ollama(model=LLM_CHAT_MODEL)

qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)
qa.combine_documents_chain.llm_chain.prompt = review_prompt

# while True:
#     question = input("Ask a question: ")
#     if question == "exit":
#         break
#     print(qa.invoke(question))

