#!/bin/bash

apt update && apt install -y curl

# Start Ollama in the background
/bin/ollama serve &

# Wait for Ollama to be ready
echo "Starting Ollama..."
until curl -s http://localhost:11434 > /dev/null; do
  sleep 1
done
echo "Ollama is ready!"

# Define the list of models to pull
MODELS="smollm2:135m" # Add or remove models as needed

# Pull and install models, or skip if they're already present
for MODEL in $MODELS; do
  if ! ollama list | grep -q "$MODEL"; then
    echo "⚡️ Pulling model: $MODEL"
    ollama pull "$MODEL"
  else
    echo "✅ Model already present: $MODEL"
  fi
done

# Wait for the Ollama server process to finish (optional, depends on your use case)
wait $!