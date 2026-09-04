from dotenv import load_dotenv
import os

# Azure OpenAI configuration

load_dotenv()
AZURE_OPENAI_API_KEY = os.getenv("API_KEY")

# AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
AZURE_OPENAI_API_VERSION = "2023-05-15"
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")

# Deployment names
CHAT_DEPLOYMENT_NAME = os.environ.get("CHAT_DEPLOYMENT_NAME", "")
EMBEDDING_DEPLOYMENT_NAME = os.environ.get("EMBEDDING_DEPLOYMENT_NAME", "")

# for VectorDB
QDRANT_URL = os.environ.get("QDRANT_URL", "")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY", "")
