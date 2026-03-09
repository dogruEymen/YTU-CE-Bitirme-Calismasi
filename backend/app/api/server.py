from pydantic import BaseModel
from fastapi import FastAPI

class ChatRequest(BaseModel):
    message: str
class ChatResponse(BaseModel):
    modelResponse: str

app = FastAPI()

# API endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(msg: ChatRequest):
    mock_answer = "coming soon ..."
    return { "modelResponse" : mock_answer }


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
