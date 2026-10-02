# Local Service Configuration

Both configuration modules read deployment details and credentials from environment variables.
Set these locally, or in an ignored `.env` file:

```dotenv
API_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
CHAT_DEPLOYMENT_NAME=your-chat-deployment
EMBEDDING_DEPLOYMENT_NAME=your-embedding-deployment
QDRANT_URL=https://your-qdrant-endpoint
QDRANT_API_KEY=your-qdrant-key
```

No original deployment endpoint or API key is required to read the examples. Running the
application requires services you control and may incur API charges. Migration validation
does not contact the original services or exercise message-sending agents.

The exposed historical Qdrant key must be revoked/replaced by its owner. History cleanup
alone does not invalidate it. Do not paste a replacement credential into issues or commits.
