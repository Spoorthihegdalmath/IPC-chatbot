from langchain_community.embeddings import CohereEmbeddings
from langchain_community.llms import Cohere
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

def setup_ipc_qa(file_path="ipc.pdf"):
    """
    Sets up the Question-Answering chain for the IPC PDF document.
    """
    cohere_api_key = os.getenv("COHERE_API_KEY")
    if not cohere_api_key:
        raise ValueError("COHERE_API_KEY environment variable not set.")
    
    embeddings = CohereEmbeddings(
        cohere_api_key=cohere_api_key,
        model="embed-english-v3.0",
        truncate="END",
        user_agent="langchain-app"
    )
    
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    text_splitter = CharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    texts = text_splitter.split_documents(documents)
    
    db = FAISS.from_documents(texts, embeddings)
    
    llm = Cohere(
        cohere_api_key=cohere_api_key,
        temperature=0.7
    )

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever()
    )

try:
    ipc_qa = setup_ipc_qa()
    print("IPC QA system initialized successfully.")
except Exception as e:
    print(f"Error initializing IPC QA system: {e}")
    print("Please ensure 'ipc.pdf' exists and COHERE_API_KEY is set in your .env file.")
    ipc_qa = None

if __name__ == "__main__":
    if ipc_qa:
        # Queries designed to elicit IPC section information related to punishments
        punishment_queries = [
            "What is the punishment for murder under IPC?",
            "What punishment is prescribed for theft in the IPC?",
            "What is the penalty for cheating according to the IPC?",
            "If someone causes grievous hurt, what section of IPC applies and what is the punishment?",
            "What are the punishments for criminal breach of trust under the Indian Penal Code?",
            "What is the punishment for rash driving under IPC?",
            "Punishment for abetment of suicide in IPC.",
            "What is the maximum punishment for rape under IPC Section 376?", # More specific
            "Describe the punishment for voluntarily causing hurt in IPC.",
            "Tell me about the punishment for criminal conspiracy."
        ]

        print("\n--- Testing Punishment Queries ---")
        for query in punishment_queries:
            normalized_query = query.lower() 
            print(f"\nQuery (original): '{query}'")
            print(f"Query (normalized): '{normalized_query}'")
            
            try:
                response = ipc_qa.run(normalized_query)
                print("Response:")
                print(response)
            except Exception as e:
                print(f"Error processing query '{query}': {e}")
    else:
        print("\nQA system not initialized. Cannot process queries.")