from langchain_openai import AzureOpenAIEmbeddings  
from langchain.vectorstores.azuresearch import AzureSearch  
from langchain.document_loaders import AzureBlobStorageContainerLoader  
from langchain.text_splitter import RecursiveCharacterTextSplitter  
from settings import get_settings
  

# Obtener configuraciones desde settings.py  
settings = get_settings()  
  
# Initialize OpenAI embeddings with Azure    
embeddings: AzureOpenAIEmbeddings = AzureOpenAIEmbeddings(
    api_version=settings.azure_openai_api_version,
    azure_endpoint=settings.azure_openai_endpoint,
    api_key=settings.azure_openai_api_key,
    azure_deployment='text-embedding-3-small',
    model='text-embedding-3-small'
)
  
# Initialize Azure Search vector store 
vector_store_address: str = f"https://{settings.azure_search_name}.search.windows.net"
vector_store: AzureSearch = AzureSearch(
    azure_search_endpoint=vector_store_address,
    azure_search_key=settings.azure_search_api_key,
    index_name=settings.azure_search_index_name,
    embedding_function=embeddings.embed_query
)
  
# Load documents from Azure Blob Storage  
conn_str: str = settings.azure_storage_connection_string  
loader: AzureBlobStorageContainerLoader = AzureBlobStorageContainerLoader(  
    conn_str=conn_str,  
    container=settings.azure_storage_container_name
)  
  
def update_knowledge_base(force_update: bool = False):  
    """  
    Verifica si la base de conocimientos ya tiene documentos. 
    Si no tiene o se fuerza, carga los documentos desde Azure Blob Storage y los sube al vector store Azure AI Search.
    """  
    # Verificar si ya hay documentos en el vector store  
    existing_documents = vector_store.similarity_search("test", k=1)  # Realiza una busqueda de prueba  
    if existing_documents and force_update == False:
        print("✅ La base de conocimientos ya tiene documentos. No se requiere actualización.")  
        return
  
    # Si no hay documentos, cargar y procesar los nuevos  
    print("⚠️ La base de conocimientos está vacía. Cargando documentos...")
    documents: list = loader.load()  
    text_splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)  
    splitted_documents = text_splitter.split_documents(documents=documents)  
  
    # Subir los documentos al vector store  
    vector_store.add_documents(documents=splitted_documents)  
    print("✅ Base de conocimientos actualizada con éxito.")