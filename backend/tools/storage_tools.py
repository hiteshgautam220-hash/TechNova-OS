import os
import json
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions

load_dotenv()

CONTAINER_NAME = "chat-history"

# --- AZURE BLOB STORAGE (UI MEMORY & TAGGING) ---
def get_blob_service_client():
    conn_str = os.environ.get("AZURE_BLOB_CONNECTION_STRING")
    if not conn_str:
        raise ValueError("AZURE_BLOB_CONNECTION_STRING not found in .env")
    return BlobServiceClient.from_connection_string(conn_str)

def upload_chat_to_blob(session_id: str, chat_json: str, tag: str = "General"):
    client = get_blob_service_client()
    container = client.get_container_client(CONTAINER_NAME)
    if not container.exists():
        container.create_container()
    
    blob_client = container.get_blob_client(f"{tag}_{session_id}.json")
    # Save the JSON and attach the tag as Azure Metadata!
    blob_client.upload_blob(chat_json, overwrite=True, metadata={"category": tag})

def download_chat_from_blob(session_id: str, tag: str = "General") -> str:
    try:
        client = get_blob_service_client()
        container = client.get_container_client(CONTAINER_NAME)
        if not container.exists():
            return "[]"
        
        blob_client = container.get_blob_client(f"{tag}_{session_id}.json")
        if not blob_client.exists():
            return "[]"
        
        return blob_client.download_blob().readall().decode("utf-8")
    except Exception:
        return "[]"

# --- CHROMADB (AI SEMANTIC MEMORY) ---
try:
    azure_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        api_base=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        api_type="azure",
        api_version="2024-02-01",
        model_name=os.environ.get("EMBEDDING_DEPLOYMENT_NAME", "text-embedding-3-small")
    )

    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name="technova_memory", embedding_function=azure_ef)
except Exception as e:
    print(f"ChromaDB init error: {e}")
    collection = None

def save_to_chroma(session_id: str, chat_json: str, tag: str):
    if not collection: return
    messages = json.loads(chat_json)
    if not messages: return
    
    chat_text = f"Session: {session_id} | Category: {tag} | "
    for m in messages:
        chat_text += f"{m['role']}: {m['content']} "
        
    collection.upsert(
        documents=[chat_text],
        metadatas=[{"session_id": session_id, "tag": tag}],
        ids=[session_id]
    )

def search_chroma(query: str) -> str:
    if not collection: return ""
    try:
        results = collection.query(query_texts=[query], n_results=1)
        if results and results['documents'] and results['documents'][0]:
            return results['documents'][0][0]
    except Exception:
        pass
    return ""

def list_chats_from_blob():
    try:
        client = get_blob_service_client()
        container = client.get_container_client(CONTAINER_NAME)
        if not container.exists():
            return []
        results = []
        for blob in container.list_blobs():
            name = blob.name.replace(".json", "")
            if "_" in name:
                tag, session = name.split("_", 1)
                results.append({"tag": tag, "session_id": session})
            else:
                results.append({"tag": "General", "session_id": name})
        return results
    except Exception:
        return []

def delete_chat_from_blob(session_id: str, tag: str = "General"):
    try:
        client = get_blob_service_client()
        container = client.get_container_client(CONTAINER_NAME)
        blob_name = f"{tag}_{session_id}.json"
        blob = container.get_blob_client(blob_name)
        blob.delete_blob()
    except Exception as e:
        print(f"Error deleting blob: {e}")
