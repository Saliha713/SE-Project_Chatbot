import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import QueryRequest
from storage import ensure_index, search
from ingestion import ingest_pdf_bytes
from embedding import embedder
from memory import get_memory, update_memory
from llm import ask_groq
from config import AUTO_INGEST_PATH, TOP_K, REQUIRED_DETAILS

app = FastAPI(title="Airline RAG Chatbot API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load FAISS index at startup
ensure_index()
if os.path.exists(AUTO_INGEST_PATH):
    ingest_pdf_bytes(open(AUTO_INGEST_PATH, "rb").read(), AUTO_INGEST_PATH)

# ------------------- Endpoints -------------------

@app.get("/")
def root():
    return {"message": "Airline RAG backend is running!"}

@app.post("/ingest")
async def upload(file: UploadFile = File(...)):
    chunks = ingest_pdf_bytes(await file.read(), file.filename)
    return {"ingested_chunks": chunks}

@app.post("/query")
async def handle_query(req: QueryRequest):
    if embedder is None:
        raise HTTPException(400, "Embedding model not loaded")

    # Retrieve top-k context from FAISS
    q_vec = embedder.encode([req.query], convert_to_numpy=True).astype("float32")
    results = search(q_vec, req.top_k)
    results = results[:3]  # limit context to top 3 chunks

    # Get session memory
    memory = get_memory(req.session_id)

    # Build system prompt
    system_prompt = (
        "You are an Airline Assistant chatbot.\n"
        "- Answer concisely.\n"
        "- Ask for missing details only if needed.\n"
        "- Provide step-by-step instructions when the user explicitly requests it.\n"
        "- Use retrieved document snippets for reference.\n"
        "- Maintain a friendly, conversational tone.\n"
    )

    # Include conversation history
    memory_text = "\n".join([f"User: {m['user']}\nBot: {m['bot']}" for m in memory.get("history", [])])
    context = "\n".join([f"[Page {r['page']}] {r['text_snippet']}" for r in results])

    # Determine if user explicitly asked for instructions
    user_wants_instructions = any(
        phrase in req.query.lower() for phrase in ["booking details", "how to book", "give me details", "booking steps"]
    )

    # Determine missing details
    missing_details = [d for d in REQUIRED_DETAILS if d not in memory.get("provided_details", {})]

    # Build user prompt
    if user_wants_instructions or not missing_details:
        # Provide instructions directly
        memory["stage"] = "provide_instructions"
        user_prompt = (
            f"{memory_text}\n\nContext:\n{context}\n\n"
            f"User question: {req.query}\n\n"
            "Bot: Provide clear, concise step-by-step instructions for booking the flight."
        )
    else:
        # Ask only the first missing detail
        detail_to_ask = missing_details[0]
        memory["stage"] = "ask_details"
        user_prompt = (
            f"{memory_text}\n\nContext:\n{context}\n\n"
            f"User question: {req.query}\n\n"
            f"Bot: Ask the user for their {detail_to_ask} in a concise, friendly way."
        )

    # Get response from LLM
    output = ask_groq(system_prompt, user_prompt)
    if not output:
        output = "Sorry, I don't know the answer."

    # Update memory
    update_memory(req.session_id, req.query, output, memory)

    return {"answer": output, "sources": results}
