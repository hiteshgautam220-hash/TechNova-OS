import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "backend" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "technova_business.db"

# Load environment variables
load_dotenv(BASE_DIR / ".env")

class Settings(BaseModel):
    EXECUTION_MODE: str = os.getenv("EXECUTION_MODE", "local").lower()
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "8501"))
    
    # Microsoft Foundry / Azure OpenAI
    PROJECT_ENDPOINT: str = os.getenv("PROJECT_ENDPOINT", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    MODEL_DEPLOYMENT_NAME: str = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o-mini-business")
    OPENAI_API_VERSION: str = os.getenv("OPENAI_API_VERSION", "2024-08-01-preview")
    
    # Responsible AI & Governance Policies
    HUMAN_APPROVAL_THRESHOLD_USD: float = float(os.getenv("HUMAN_APPROVAL_THRESHOLD_USD", "500.0"))
    MAX_DISCOUNT_PERCENT: float = float(os.getenv("MAX_DISCOUNT_PERCENT", "15.0"))
    AUTO_REFUND_ALLOWED: bool = os.getenv("AUTO_REFUND_ALLOWED", "false").lower() == "true"
    
    # Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = DATA_DIR
    DB_PATH: Path = DB_PATH
    CUSTOMERS_CSV: Path = DATA_DIR / "customers.csv"
    PRODUCTS_CSV: Path = DATA_DIR / "products.csv"
    ORDERS_CSV: Path = DATA_DIR / "orders.csv"
    RETURNS_CSV: Path = DATA_DIR / "returns.csv"
    POLICIES_JSON: Path = DATA_DIR / "policies.json"

settings = Settings()
