from langchain.retrievers import AzureCognitiveSearchRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import AzureChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain.callbacks import get_openai_callback
from datetime import datetime, timezone
from settings import get_settings  # Importar configuraciones centralizadas


# Obtener configuraciones desde settings.py  
settings = get_settings()


def initialize_rag_chat_chain():
    """  
    Inicializa una cadena conversacional RAG (Retrieval-Augmented Generation) personalizada  
    para un asistente virtual llamado "Ingenierin".  
    """
    # Template para reformular preguntas con historial de chat  
    contextualize_retriever_system_prompt: str = '''  
    Tu tarea es reformular preguntas para mejorar la recuperación de información en un sistema de RAG.  
    Dado un historial de conversación y la última pregunta del usuario —la cual podría depender del contexto previo—,  
    reformula la pregunta para que sea completamente independiente y comprensible por sí sola, sin necesidad del historial.  
    No respondas la pregunta. Si ya es clara y autónoma, simplemente devuélvela sin cambios.  
    Si requiere contexto del historial para entenderse, incorpora la información necesaria en la reformulación  
    de forma concisa y coherente.  
    '''  
    contextualized_retriever_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages([  
        ('system', contextualize_retriever_system_prompt),  
        MessagesPlaceholder('chat_history'),  
        ('human', '{input}')  
    ])  
  
    # Prompt del asistente con personalidad definida  
    template: str = '''  
      Eres un asistente llamado "Ingenierin", diseñado para atender las consultas de estudiantes de una fundación  
      dedicada a la formación de profesionales emprendedores en tiendas, minimarkets y pequeños negocios.  
      Tu propósito es brindar orientación clara, útil y específica sobre temas de logística, gestión de inventario,  
      bodegaje y reabastecimiento. Ten en cuenta estas instrucciones para responder:  
      1. Utiliza un lenguaje formal pero cercano y amigable, adecuado para un entorno educativo y práctico.
      2. Incluye emojis relevantes para hacer las respuestas más visuales y comprensibles.  
      3. Limita tus respuestas exclusivamente a temas relacionados con logística, finanzas, inventario, bodegaje y reabastecimiento.  
        Si la consulta está fuera de estos temas, informa amablemente que no puedes responderla, pero se breve.  
      {context}  
      \n\n  
      Pregunta: {question}  
      Respuesta:  
    '''  
    prompt: PromptTemplate = PromptTemplate(template=template, input_variables=['context', 'question'])  
  
    # Inicializar llm  
    llm: AzureChatOpenAI = AzureChatOpenAI(  
        api_version=settings.azure_openai_api_version,  
        azure_endpoint=settings.azure_openai_endpoint,  
        api_key=settings.azure_openai_api_key,  
        azure_deployment=settings.azure_openai_deployment_name,  
        deployment_name='chat'  
    )  
  
    # Inicializar el retriever  
    retriever: AzureCognitiveSearchRetriever = AzureCognitiveSearchRetriever(  
        service_name=settings.azure_search_name,  
        index_name=settings.azure_search_index_name,  
        api_key=settings.azure_search_api_key,  
        content_key='content',  
        top_k=10  
    )  
  
    # Inicializar memoria de conversación  
    chat_memory: ConversationBufferMemory = ConversationBufferMemory(  
        memory_key="chat_history",  
        return_messages=True  
    )  
  
    # Cadena conversacional RAG  
    rag_chain: ConversationalRetrievalChain = ConversationalRetrievalChain.from_llm(  
        llm=llm,  
        memory=chat_memory,  
        retriever=retriever,  
        combine_docs_chain_kwargs={'prompt': prompt}  
    )

    return rag_chain  
  

# Función para generar la respuesta del modelo  
def generate_response(rag_chain, user_question: str, session_id: str) -> str:  
    """  
    Genera la respuesta del modelo basada en la pregunta del usuario.  
    """  
    try:  
        # Ejecutar la cadena conversacional para obtener la respuesta  
        response = rag_chain.run(question=user_question)  
        return response
    except Exception as e:  
        raise Exception(f"Error al generar la respuesta: {str(e)}")  


# Función para generar los logs  
def generate_logs(rag_chain, user_question: str, session_id: str) -> dict:  
    """  
    Genera los logs relacionados con la interacción.  
    """  
    try:  
        # Ejecutar la cadena conversacional con registro de costos  
        with get_openai_callback() as cb:  
            response = rag_chain.run(question=user_question)  
  
            # Diccionario de logs  
            logs = {  
                "session_id": session_id,  
                "total_tokens": cb.total_tokens,  
                "prompt_tokens": cb.prompt_tokens,  
                "completion_tokens": cb.completion_tokens,  
                "total_cost_usd": cb.total_cost,  
                "user_question": user_question,  
                "llm_answer": response,  
                "date_processed": datetime.now(timezone.utc).isoformat()  
            }  
        return logs  
    except Exception as e:  
        raise Exception(f"Error al generar los logs: {str(e)}")