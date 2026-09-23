import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

def extract_text_from_document(file_bytes: bytes) -> str:
    endpoint = os.environ.get("DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.environ.get("DOCUMENT_INTELLIGENCE_KEY")
    if not endpoint or not key:
        return "[Error: Document Intelligence credentials not found in .env]"
    
    try:
        client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        poller = client.begin_analyze_document("prebuilt-read", document=file_bytes)
        result = poller.result()
        
        text = ""
        for page in result.pages:
            for line in page.lines:
                text += line.content + "\n"
        return text.strip()
    except Exception as e:
        return f"[Error extracting document: {str(e)}]"
