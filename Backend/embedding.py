from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from config import EMBED_MODEL

embedder = SentenceTransformer(EMBED_MODEL)
VECTOR_DIM = embedder.get_sentence_embedding_dimension()

def embed_text(chunks):
    vectors = embedder.encode(chunks, convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(vectors)
    return vectors
