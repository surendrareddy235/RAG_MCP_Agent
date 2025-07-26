# api/main.py

import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
from agents.ingestion_agent import IngestionAgent
from agents.retrieval_agent import RetrievalAgent
from agents.llm_response_agent import LLMResponseAgent
from mcp.protocol import MCPMessage

app = FastAPI()

# Allow CORS for frontend (e.g., Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Agent instances ===
ingestion_agent = IngestionAgent()
retrieval_agent = RetrievalAgent()
llm_response_agent = LLMResponseAgent()

UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/process")
async def process_files(
    files: list[UploadFile] = File(...),
    query: str = Form(...),
    history: str = Form(default="[]")
):
    import ast
    chat_history = ast.literal_eval(history)

    file_paths = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        file_paths.append(file_path)

    # Step 1: IngestionAgent
    msg1 = MCPMessage(
        sender="UI",
        receiver="IngestionAgent",
        type="DOCUMENT_UPLOAD",
        payload={"file_paths": file_paths, "query": query, "history": chat_history}
    )
    parsed_msg = ingestion_agent.handle(msg1)

    # Step 2: RetrievalAgent
    retrieval_msg = retrieval_agent.handle(parsed_msg)

    # Step 3: LLMResponseAgent (pass history)
    retrieval_msg.payload["history"] = chat_history
    response_msg = llm_response_agent.handle(retrieval_msg)

    return JSONResponse(content=response_msg.to_dict())
