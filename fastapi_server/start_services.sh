#!/bin/bash
#ollama serve &
## Save the PID of the process
#PID=$!
## Wait for the process to complete
#wait $PID

ollama run llama2 &
# Save the PID of the process
PID=$!
# Wait for the process to complete
wait $PID

# test ollama works
curl -v http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "3 + 10=?",
  "stream": false
}'

# After the first process completes, start the second service
uvicorn fastapi_server.app:app --host 0.0.0.0 --port 90 --workers 4
