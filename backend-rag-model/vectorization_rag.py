from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
import os


from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.vectorstores import FAISS

from langchain.chains import ConversationalRetrievalChain




documents = []

for file in os.listdir('data/clean_data/'):
    if file.endswith('.txt'):
        path = './data/clean_data/'+ file
        loaders = TextLoader(path, encoding='utf-8')
        documents.extend(loaders.load())






splt_text = CharacterTextSplitter(chunk_size=500, chunk_overlap=80)
split_documents = splt_text.split_documents(documents)


llm = OllamaLLM(model='llama3')

vector_db = FAISS.load_local(
    './data/vector_store',
    embeddings=OllamaEmbeddings(model='nomic-embed-text'),
    allow_dangerous_deserialization=True
)



qa_retrieval = ConversationalRetrievalChain.from_llm(
    llm, 
    vector_db.as_retriever(search_kwargs={'k':6}),
    return_source_documents =True
)


