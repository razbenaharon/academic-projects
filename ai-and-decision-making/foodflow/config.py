"""
Centralized configuration for Azure OpenAI and Qdrant.
Prefer environment variables over hardcoding credentials.

If using a `.env` file, ensure it's not committed and contains:
  API_KEY=...
"""
from dotenv import load_dotenv
import os

# Load environment variables from .env if present
load_dotenv()

# === Azure OpenAI configuration ===
AZURE_OPENAI_API_KEY = os.getenv("API_KEY")

# Consider updating to the latest stable API version when applicable
# AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
AZURE_OPENAI_API_VERSION = "2023-05-15"
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")

# Deployment names (must exist in your Azure OpenAI resource)
CHAT_DEPLOYMENT_NAME = os.environ.get("CHAT_DEPLOYMENT_NAME", "")
EMBEDDING_DEPLOYMENT_NAME = os.environ.get("EMBEDDING_DEPLOYMENT_NAME", "")

# === Qdrant configuration ===
# TIP: Store these in environment variables instead of hardcoding.
QDRANT_URL = os.environ.get("QDRANT_URL", "")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY", "")
