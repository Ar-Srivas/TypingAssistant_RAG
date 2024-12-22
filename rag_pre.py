import PyPDF2
import faiss
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore
import numpy as np
from huggingface_hub import InferenceClient

embedding_model = SentenceTransformer('multi-qa-mpnet-base-dot-v1')

repo_id = "microsoft/Phi-3.5-mini-instruct"

client = InferenceClient(
    api_key="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",
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
        embedding_function=embeddings,
        index=faiss_index,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id
    )
    
    return faiss_vector_store

def create_vectorspace(pdf):
    pdf_read = PyPDF2.PdfReader(pdf)
    text = pdf_to_text(pdf_read)
    chunks = create_chunks(text, pdf_read)
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

def get_suggestion(client, query, faiss_index):
    embedded_query = embedding_model.encode([query])
    distances, indices = faiss_index.index.search(embedded_query, k=3)
    docs = []
    for i in indices[0]:
        docs.append(faiss_index.docstore.search(i))
    context = " ".join(docs)
    return send_to_llm(client, query, context)