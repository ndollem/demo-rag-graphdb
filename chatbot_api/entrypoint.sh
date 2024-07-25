#!/bin/bash

# Load environment variables
set -a
source .env
set +a

# Run any setup steps or pre-processing tasks here
echo "Starting Document RAG FastAPI service..."

# Start the main application
uvicorn chatbot_api.main:app --host 0.0.0.0 --port 8000