import os
from azure.identity import AzureCliCredential
from agent_framework.foundry import FoundryChatClient
from dotenv import load_dotenv

load_dotenv()

# Hotfix: Force Python to know where Azure CLI is installed since it isn't in your system PATH yet
azure_cli_path = r'C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin'
if azure_cli_path not in os.environ.get('PATH', ''):
    os.environ['PATH'] = azure_cli_path + os.pathsep + os.environ.get('PATH', '')

_client = FoundryChatClient(
    project_endpoint=os.environ.get('FOUNDRY_PROJECT_ENDPOINT', ''),
    model=os.environ.get('FOUNDRY_MODEL', ''),
    credential=AzureCliCredential(),
)

def get_foundry_client():
    return _client

