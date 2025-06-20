import uuid
import libsql
from settings import get_settings


settings = get_settings()

TURSO_API_TOKEN: str = settings.turso_api_token
TURSO_DATABASE_URL: str = settings.database_url

# Verificar que las credenciales estén configuradas
if not TURSO_DATABASE_URL or not TURSO_API_TOKEN:
    raise Exception("TURSO_DATABASE_URL o TURSO_API_TOKEN no estan configurados.")


def get_db_connection():  
    """Obtiene la conexión a la base de datos Turso."""
    return libsql.connect(database=TURSO_DATABASE_URL, auth_token=TURSO_API_TOKEN)


# Crear la tabla en Turso si no existe
def init_db(verbose: bool = False):
    """Inicializa la base de datos Turso y crea la tabla de logs si no existe."""
    try:
        conn = get_db_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                ID TEXT PRIMARY KEY,
                session_id TEXT,
                total_tokens INTEGER,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                total_cost_usd REAL,
                user_question TEXT,
                llm_answer TEXT,
                date_processed TEXT
            );
        """)
        if verbose:
          print("✅ Base de datos existe o fue creada con exito.")
    except Exception as e:
        raise Exception(f"Error al inicializar la base de datos: {str(e)}")


def store_logs(costs_logs: dict, verbose: bool = False):
    """  
    Almacena los logs en la base de datos Turso.  
      
    Args:  
        costs_logs (dict): Diccionario con los datos de los logs.
    """  
    try:  
        conn = get_db_connection()  
        unique_id = str(uuid.uuid4())  # Generar un identificador único para el registro  
        conn.execute("""  
            INSERT INTO logs (ID, session_id, total_tokens, prompt_tokens, completion_tokens, total_cost_usd, user_question, llm_answer, date_processed)  
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);  
        """, (  
            unique_id,  # Identificador único  
            costs_logs["session_id"],  
            costs_logs["total_tokens"],  
            costs_logs["prompt_tokens"],  
            costs_logs["completion_tokens"],  
            costs_logs["total_cost_usd"],  
            costs_logs["user_question"],  
            costs_logs["llm_answer"],  
            costs_logs["date_processed"]  
        ))
        conn.commit()
        if verbose:
          print("✅ Logs almacenados con éxito.")
    except Exception as e:  
        raise Exception(f"Error al almacenar los logs: {str(e)}")