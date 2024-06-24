from Models.modelComditionalsInFile import *
from langchain_community.llms import Ollama
from langchain import PromptTemplate
import re


def isConditions(path) :
    # Loading orca-mini from Ollama
    llm = Ollama(model="llama3:8b", temperature=0)

    # Loading the Embedding Model
    embed = load_embedding_model(model_path="all-MiniLM-L6-v2")

    # loading and splitting the documents
    docs = load_pdf_data(file_path=path)
    documents = split_docs(documents=docs)

    # creating vectorstore
    vectorstore = create_embeddings(documents, embed)

    # converting vectorstore to a retriever
    retriever = vectorstore.as_retriever()

    # Creating the prompt from the template which we created before
    prompt = PromptTemplate.from_template(template)

    # Creating the chain
    chain = load_qa_chain(retriever, llm, prompt)

    responceFirst = get_response('Whether this file is news or a government decree or other official document. Answer only true or false', chain)

    return responceFirst