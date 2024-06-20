from Models.modelComditionalsInFile import *
from langchain_community.llms import Ollama
from langchain import PromptTemplate
import re


def getConditionals(path) :
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

    responceFirst = get_response('Какие условия участия в данной программе? Ответ приведи ввиде списка и на русском языке. Предоставь мне только список без твоих мыслей и расмышлений не нужно придумывать условия, только на основании текса. ', chain)

    responce = responceFirst.replace('\n', ' ')

    pattern = r'\d+\.\s'
    segments = re.split(pattern, responce)[1:]

    # Восстановление разделителей
    segments = [f'{i+1}. {segment.strip()}' for i, segment in enumerate(segments)]
    return segments