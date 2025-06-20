"""Configuration settings for Azure AI Chatbot"""

import os
from typing import List
from pydantic_settings import BaseSettings


# Intentar importar userdata para Google Colab
try:
    from google.colab import userdata
    IS_COLAB = True
except ImportError:
    IS_COLAB = False


class Settings(BaseSettings):
    """Application settings"""

    # Application Configuration
    app_name: str = "Azure AI Chatbot"
    environment: str = os.getenv("ENVIRONMENT", "development")
    port: int = int(os.getenv("PORT", "8000"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # CORS Configuration
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://bda-chatbot-frontend-e4ddbvftcmcjbvd3.chilecentral-01.azurewebsites.net",
    ]

    # Azure OpenAI Configuration
    if IS_COLAB:
        azure_openai_api_key: str = userdata.get('azure_api_key')
        azure_openai_endpoint: str = userdata.get('azure_endpoint')
        azure_openai_deployment_name: str = userdata.get('azure_llm_deployment')
        azure_openai_api_version: str = userdata.get('azure_api_version')
    else:
        azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
        azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        azure_openai_deployment_name: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
        azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

    # Azure AI Search Configuration
    if IS_COLAB:
        azure_search_endpoint: str = f"https://{userdata.get('azure_cognitive_search_name')}.search.windows.net"
        azure_search_api_key: str = userdata.get('azure_cognitive_search_api_key')
        azure_search_index_name: str = userdata.get('azure_cognitive_search_index_name')
        azure_search_name: str = userdata.get('azure_cognitive_search_name')

    else:
        azure_search_endpoint: str = os.getenv("AZURE_SEARCH_ENDPOINT", "")
        azure_search_api_key: str = os.getenv("AZURE_SEARCH_API_KEY", "")
        azure_search_index_name: str = os.getenv("AZURE_SEARCH_INDEX_NAME", "knowledge-base")
        azure_search_name: str = os.getenv('AZURE_SEARCH_NAME')

    # Azure Blob Storage Configuration
    if IS_COLAB:
        azure_storage_connection_string: str = f"DefaultEndpointsProtocol=https;AccountName={userdata.get('azure_storage_account_name')};AccountKey={userdata.get('azure_storage_account_api_key')};EndpointSuffix={userdata.get('azure_storage_account_endpoint_suffix')}"
        azure_storage_container_name: str = userdata.get('azure_storage_account_container_name')
    else:
        azure_storage_connection_string: str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
        azure_storage_container_name: str = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "documents")

    # Database Configuration
    if IS_COLAB:
        database_url: str = userdata.get('turso_database_url')
        turso_api_token: str = userdata.get('turso_auth_token')
    else:
        database_url: str = os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")
        turso_api_token: str = os.getenv("TURSO_API_TOKEN", "")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
_settings = None

def get_settings() -> Settings:
    """Get application settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def validate_azure_settings():
    """Validate required Azure environment variables"""
    settings = get_settings()

    required_vars = [
        ("AZURE_OPENAI_API_KEY", settings.azure_openai_api_key),
        ("AZURE_OPENAI_ENDPOINT", settings.azure_openai_endpoint),
        ("AZURE_SEARCH_ENDPOINT", settings.azure_search_endpoint),
        ("AZURE_SEARCH_API_KEY", settings.azure_search_api_key),
        ("TURSO_DATABASE_URL", settings.database_url),
        ("TURSO_API_TOKEN", settings.turso_api_token),
    ]

    # Identificar variables faltantes  
    missing = [var_name for var_name, value in required_vars if not value]  
  
    # Si faltan variables, lanzar una excepción  
    if missing:  
        missing_vars = ", ".join(missing)  
        raise RuntimeError(  
            f"⚠️ Faltan las siguientes variables de entorno requeridas: {missing_vars}. "  
            "Verifica la configuración antes de continuar."  
        )  
  
    # Si todas las variables están configuradas, imprimir un mensaje de éxito  
    print("✅ Todas las variables de entorno de Azure están configuradas correctamente.")  
    return True 