from Models.modelComditionalsInFile import *
from langchain_community.llms import Ollama
from langchain import PromptTemplate
import re


def isConditions(path) :
    # Loading orca-mini from Ollama
    llm = Ollama(model="mistral", temperature=0)

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

    responceFirst = get_response('Я вляется ли этот файл новостью или постановлением правительства для госпрограммы. Ответь только true или false ', chain)

    return responceFirst