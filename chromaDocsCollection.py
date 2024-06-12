from langchain_community.vectorstores import Chroma
from chromadb.config import Settings
from langchain_community.embeddings import OllamaEmbeddings

# settings = Settings(
#     embedding_function=,
# )
chroma_client = Chroma(
    embedding_function=OllamaEmbeddings(model="nomic-embed-text"),
    persist_directory='chroma',
    collection_name='documents'
)