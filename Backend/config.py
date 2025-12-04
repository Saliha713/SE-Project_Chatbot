import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
TOP_K = int(os.getenv("TOP_K", 4))
MEMORY_SIZE = int(os.getenv("MEMORY_SIZE", 5))
AUTO_INGEST_PATH = os.getenv("AUTO_INGEST_PATH", "documents/AirXpert_Airlines_Policies.pdf")
# Required details for booking
REQUIRED_DETAILS = ["departure_city", "destination_city", "travel_dates", "passengers"]

INDEX_DIR = "faiss_index"
VECTOR_DIM = None  # will be set after embedding model loads
