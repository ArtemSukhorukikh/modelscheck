from chromaDocsCollection import chroma_client
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever

def index(localPath):
    loader = PyPDFLoader(localPath)
    pages = loader.load_and_split()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2500, chunk_overlap=100)
    chunks = text_splitter.split_documents(pages)
    chroma_client.add_documents(documents=chunks)
 
    # LLM from Ollama
    local_model = "llama3:8b-instruct-q8_0"
    llm = ChatOllama(model=local_model)
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""Вы - ассистент по языковой модели искусственного интеллекта для ответа по законодательному документу.
        Не нужно придумывать своих условий или что-то подобное, только что представленно в тексте.
        Ваша задача - найти информацию из текста документа условия участия и только их.
        Никакой другой или вводной информации не надо. 
        Отвечай только на русском языке для этого.
        Пример ответа <start>Необходимо быть резедентом РФ</end><start>Текст второго условия</end>
        Исходный вопрос: {question}""",
    )
    retriever = MultiQueryRetriever.from_llm(
        chroma_client.as_retriever(), 
        llm,
        prompt=QUERY_PROMPT
    )

    # RAG prompt
    template = """Отвечай на вопросы без вводной инфформации согласно контексту.  
    Только список сразу на русском языке. Формат ответа слудующий его нарушить нельзя! 1.текст условия 2.текст условия.
    {context}
    Вопрос: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    response = chain.invoke("Какие условия участия в программе представленном в данном файле?")
    return response.split('\n')
