from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
from agent import chat

app = FastAPI(title="Skylark BI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

# Allow flexible chart data
class ChatResponse(BaseModel):
    reply: str
    chartData: Optional[Dict[str, Any]] = None

@app.get("/")
def root():
    return {"status": "Skylark BI Agent is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]

        result = chat(messages)

        # Safe extraction
        reply = result.get("reply", "")
        chart_data = result.get("chartData", None)

        return ChatResponse(
            reply=reply,
            chartData=chart_data
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)