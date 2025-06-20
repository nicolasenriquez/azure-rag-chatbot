# Azure AI Chatbot Backend  
  
## Descripción  
Este proyecto es el backend de un chatbot basado en inteligencia artificial, diseñado para proporcionar respuestas contextuales y enriquecidas utilizando tecnologías como Azure OpenAI, Azure AI Search y Turso como base de datos distribuida. El chatbot está optimizado para atender consultas relacionadas con logística, gestión de inventario, bodegaje y reabastecimiento.  
  
## Características  
- **Integración con Azure OpenAI:** Utiliza modelos generativos avanzados para responder preguntas.  
- **Azure AI Search:** Enriquecimiento de respuestas mediante búsqueda contextual.  
- **Base de datos distribuida con Turso:** Almacenamiento de logs y datos de conversación.  
- **FastAPI:** Framework ligero y rápido para la creación de APIs.  
- **Modularización:** Código organizado en módulos para facilitar el mantenimiento y escalabilidad.  
- **Despliegue automatizado:** Configuración de GitHub Actions para despliegue en Azure Web Apps.  
  
## Estructura del Proyecto  
```plaintext  
backend/  
├── .github/  
│   └── workflows/  
│       └── azure_webapps_deploy.yml  # Configuración de GitHub Actions  
├── app/  
│   ├── __init__.py                   # Inicialización del paquete  
│   ├── main.py                       # Punto de entrada principal  
│   ├── settings.py                   # Configuración centralizada  
│   ├── azure_ai_search.py            # Integración con Azure AI Search  
│   ├── chatbot_app.py                # Lógica del chatbot  
│   ├── chatbot_api.py                # Endpoints de la API  
│   ├── database.py                   # Interacción con la base de datos  
│   ├── models.py                     # Modelos de datos con Pydantic  
│   └── utils.py                      # Funciones auxiliares  
├── tests/  
│   ├── test_chatbot_api.py           # Pruebas para los endpoints  
│   ├── test_database.py              # Pruebas para la base de datos  
│   ├── test_settings.py              # Pruebas para la configuración  
│   └── test_chatbot_app.py           # Pruebas para la lógica del chatbot  
├── .env                              # Variables de entorno  
├── .gitignore                        # Archivos ignorados por Git  
├── requirements.txt                  # Dependencias del proyecto  
├── README.md                         # Documentación del proyecto  


## Requisitos  
- **Python 3.11 o superior**  
- **Azure Web Apps** para el despliegue.  
- **GitHub Actions** configurado para despliegue automatizado.  
- **Azure OpenAI** y **Azure AI Search** configurados con claves de API.  
- **Turso** como base de datos distribuida.  
  
## Instalación  
  
### 1. Clonar el repositorio  
```bash  
git clone https://github.com/tu_usuario/tu_repositorio.git  
cd backend
```

### 2. Crear un entorno virtual
```bash
python -m venv venv  
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt  
 ```

### 4. Configurar variables de entorno
Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```bash
ENVIRONMENT=development  
PORT=8000  
AZURE_OPENAI_API_KEY=tu_clave  
AZURE_OPENAI_ENDPOINT=https://tu_endpoint.openai.azure.com  
AZURE_SEARCH_ENDPOINT=https://tu_endpoint.search.windows.net  
AZURE_SEARCH_API_KEY=tu_clave  
DATABASE_URL=sqlite:///./chatbot.db  
TURSO_API_TOKEN=tu_token  
```

### Ejecutar la Aplicación
Para ejecutar el backend localmente:

```bash
uvicorn app.main:app --reload  
```
La API estará disponible en: http://localhost:8000


## Endpoints Principales 

### 1. `/api/chat`
Método: `POST`
Descripción: Genera una respuesta del chatbot y almacena los logs en la base de datos.
Ejemplo de solicitud:
```bash
{  
  "session_id": "chat_001",  
  "user_question": "¿Cómo puedo optimizar mi inventario?"  
}  
```

### 2. `/api/chat/history/{session_id}`
Método: `GET`
Descripción: Recupera el historial de una conversación específica.

### 3. `/api/chat/stats`
Método: `GET`
Descripción: Obtiene estadísticas del servicio de chat.

### 4. `/api/health`
Método: `GET`
Descripción: Verifica la salud del servicio.


## Contribución
Si deseas contribuir al proyecto:

Haz un fork del repositorio.
Crea una rama para tu funcionalidad (git checkout -b feature/nueva-funcionalidad).
Haz un commit de tus cambios (git commit -m "Añadir nueva funcionalidad").
Haz un push a tu rama (git push origin feature/nueva-funcionalidad).
Abre un Pull Request.

## Licencia
Este proyecto está bajo la licencia MIT.