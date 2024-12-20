import PyPDF2
import faiss
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore
import numpy as np
from huggingface_hub import InferenceClient
import logging
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Read the API key from the environment variable
api_key = os.getenv("RAG_API_KEY")

embedding_model = SentenceTransformer('multi-qa-mpnet-base-dot-v1')

repo_id = "microsoft/Phi-3.5-mini-instruct"

client = InferenceClient(
    api_key=api_key,
    model=repo_id,
    timeout=120,
)

def pdf_to_text(pdf):
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    return text

def chunk(pdf):
    no = len(pdf.pages)
    if no >= 3 and no <= 5:
        return 15
    elif no >= 5 and no <= 20:
        return 100
    elif no > 20 and no <= 50:
        return 200
    elif no > 50 and no <= 100:
        return 300
    else:
        return 400

def create_chunks(text, pdf):
    chunk_size = chunk(pdf)
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i+chunk_size]))
    return chunks

def embed_chunks(chunks):
    embeddings = embedding_model.encode(chunks)
    embedding_dimension = embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(embedding_dimension)
    faiss_index.add(np.array(embeddings))
    docstore = InMemoryDocstore()
    for i, chunk in enumerate(chunks):
        docstore.add({i: chunk})
    index_to_docstore_id = {i: i for i in range(len(chunks))}
    
    faiss_vector_store = FAISS(
        embedding_function=embedding_model.encode,
        index=faiss_index,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id
    )
    
    return faiss_vector_store

def create_vectorspace(pdf_stream):
    pdf = PyPDF2.PdfReader(pdf_stream)
    text = pdf_to_text(pdf)
    chunks = create_chunks(text, pdf)
    vectorDB = embed_chunks(chunks)
    return vectorDB

query_template = """Given the context: {context}\n
                    Answer the following query in one line of maximum ten words.\n
                    If you think the query is not relevant to the context, do not respond at all\n
                    The query is: {query} Do not provide any note or comments after the answer has been generated. Only give the answer and nothing else."""

def send_to_llm(inference_client: InferenceClient, query, context):
    prom = query_template.format(query=query, context=context)
    messages = [
        {"role": "system", "content": prom},
        {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
    ]
    response = inference_client.chat.completions.create(
        model=repo_id,
        max_tokens=50,
        messages=messages
    )
    return response['choices'][0]['message']['content']

def get_suggestion(client, query, vectorDB):
    try:
        logging.info(f"Processing query: {query}")
        embedded_query = embedding_model.encode([query])
        
        # Search for relevant documents
        distances, indices = vectorDB.index.search(np.array(embedded_query), k=1)
        logging.info(f"Search results - distances: {distances}, indices: {indices}")
        
        if indices.size > 0 and indices[0][0] != -1:
            # Get context from the vector store
            context_id = indices[0][0]
            context = vectorDB.docstore.search(context_id)
            logging.info(f"Found context: {context[:100]}...")  # Log first 100 chars
            
            # Generate suggestion
            suggestion = send_to_llm(client, query, context)
            logging.info(f"Generated suggestion: {suggestion}")
            
            return suggestion
        else:
            logging.warning("No relevant context found")
            return "No relevant information found"
            
    except Exception as e:
        logging.error(f"Error in get_suggestion: {e}")
        return f"Error generating suggestion: {str(e)}"