import os, json
import faiss
from config import INDEX_DIR, VECTOR_DIM

index = None
metadata = []

META_FILE = os.path.join(INDEX_DIR, "metadata.json")

def ensure_index():
    global index, metadata
    os.makedirs(INDEX_DIR, exist_ok=True)
    if index is None:
        idx_file = os.path.join(INDEX_DIR, "faiss.index")
        if os.path.exists(idx_file) and os.path.exists(META_FILE):
            index = faiss.read_index(idx_file)
            metadata = json.load(open(META_FILE, "r", encoding="utf-8"))
        else:
            index = faiss.IndexFlatIP(VECTOR_DIM)
            metadata = []

def save_index():
    faiss.write_index(index, os.path.join(INDEX_DIR, "faiss.index"))
    json.dump(metadata, open(META_FILE, "w", encoding="utf-8"), indent=2)

def search(query_vector, top_k):
    D, I = index.search(query_vector, top_k)
    return [metadata[i] for i in I[0] if i < len(metadata)]

