import json

from groq import Groq
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
load_dotenv()
import os 

# Load environment variables from .env file
api_key = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=api_key)
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
EMBEDDING_DIM = 384

splitter = SentenceSplitter(
    chunk_size=1000, 
    chunk_overlap=200,
    )

def load_and_chunk_pdf(file_path : str):
    docs = PDFReader().load_data(file_path)
    texts = [d.text for d in docs if getattr(d, 'text', None)]
    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t))
    return chunks

def embed_texts(texts : list[str]) -> list[list[float]]:
    model = EMBEDDING_MODEL
    model_dimension = model.get_sentence_embedding_dimension() 
    embeddings = model.encode(texts)
    data = {"embeddings": embeddings.tolist()}
    json_data = json.dumps(data)
    print(json_data)
    return embeddings.tolist()    
    '''
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )
    return [r.embedding for r in response.data]
    '''