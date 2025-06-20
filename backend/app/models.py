from pydantic import BaseModel


# Pydantic modelo validacion para las solicitudes de chat
class ChatRequest(BaseModel):
    session_id: str
    user_question: str

# Pydantic modelo validacion para las respuestas de chat
class ChatResponse(BaseModel):
    llm_answer: str