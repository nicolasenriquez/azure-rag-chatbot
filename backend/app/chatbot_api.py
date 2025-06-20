from typing import Optional
from datetime import datetime, timedelta
from models import ChatResponse, ChatRequest
from database import init_db, store_logs, get_db_connection
from chatbot_app import initialize_rag_chat_chain, generate_response, generate_logs
from fastapi import FastAPI, HTTPException, APIRouter, Depends, BackgroundTasks


# Inicializar la base de datos
init_db()

# Inicializar FastAPI
app = FastAPI()

# Inicializar el router
router = APIRouter()

# Inicializar cadena conversacional RAG
rag_chain = initialize_rag_chat_chain()


# Fast API
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Endpoint para interactuar con el chatbot y guardar automáticamente los logs en la base de datos.
    """
    try:
        # Generar la respuesta del modelo
        response = generate_response(rag_chain, request.user_question, request.session_id)

        # Generar los logs
        costs_logs = generate_logs(rag_chain, request.user_question, request.session_id)

        # Guardar los logs en la base de datos Turso  
        store_logs(costs_logs)

        # Programar una tarea en segundo plano para limpiar conversaciones antiguas
        background_tasks.add_task(clean_old_logs, max_age_hours=72)

        # Devolver solo la respuesta al cliente
        return ChatResponse(llm_answer=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/chat/history/{session_id}")
async def get_conversation_history(session_id: str):
    """
    Endpoint para recuperar el historial de una conversación específica.
    """
    try:
        conn = get_db_connection()
        result = conn.execute("SELECT * FROM logs WHERE session_id = ?;", (session_id,))
        logs = result.fetchall()

        if not logs:
            raise HTTPException(status_code=404, detail=f"No se encontró historial para la sesión {session_id}")

        return {"session_id": session_id, "logs": logs}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al recuperar el historial: {str(e)}")

@router.delete("/chat/history/{session_id}")
async def delete_conversation(session_id: str):
    """
    Endpoint para eliminar el historial de una conversación específica.
    """
    try:
        conn = get_db_connection()
        result = conn.execute("DELETE FROM logs WHERE session_id = ?;", (session_id,))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"No se encontró historial para la sesión {session_id}")

        return {"message": f"Historial de la sesión {session_id} eliminado exitosamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar el historial: {str(e)}")

@router.get("/chat/stats")
async def get_chat_stats():
    """
    Endpoint para obtener estadísticas del servicio de chat.
    """
    try:
        conn = get_db_connection()
        result = conn.execute("SELECT COUNT(DISTINCT session_id) AS active_sessions FROM logs;")
        active_sessions = result.fetchone()[0]

        return {
            "active_sessions": active_sessions,
            "service_status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

@router.post("/chat/cleanup")
async def cleanup_conversations(max_age_hours: int = 72):
    """Endpoint para limpiar conversaciones antiguas."""
    try:
        conn = get_db_connection()
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        conn.execute("DELETE FROM logs WHERE date_processed < ?;", (cutoff_time.isoformat(),))
        return {"message": f"Conversaciones más antiguas que {max_age_hours} horas eliminadas exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al limpiar conversaciones: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Endpoint para verificar la salud del servicio.
    """
    try:
        return {
            "status": "healthy",
            "service": "chat-service",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail="El servicio de chat no está saludable")

def clean_old_logs(max_age_hours: int):
    """
    Limpia los registros antiguos de la base de datos.
    """
    try:
        conn = get_db_connection()
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        conn.execute("DELETE FROM logs WHERE date_processed < ?;", (cutoff_time.isoformat(),))
    except Exception as e:
        print(f"Error al limpiar registros antiguos: {str(e)}")