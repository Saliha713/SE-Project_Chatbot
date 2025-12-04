from pydantic import BaseModel
from config import TOP_K

class QueryRequest(BaseModel):
    query: str
    session_id: str | None = "default"
    top_k: int = TOP_K
