from langchain_community.embeddings import CohereEmbeddings
from langchain_community.llms import Cohere  # <-- This was missing
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

def setup_doc_qa(file_path, file_type="pdf"):
    # Initialize with required parameters
    embeddings = CohereEmbeddings(
        cohere_api_key=os.getenv("COHERE_API_KEY"),
        model="embed-english-v3.0",
        truncate="END",
        user_agent="legal-research-assistant"
    )
    
    # Load document based on file type
    if file_type == "pdf":
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path)
    
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    # Create vector store
    db = FAISS.from_documents(texts, embeddings)
    
    return RetrievalQA.from_chain_type(
        llm=Cohere(  # Now properly imported
            cohere_api_key=os.getenv("COHERE_API_KEY"),
            temperature=0.7
        ),
        chain_type="stuff",
        retriever=db.as_retriever()
    )
