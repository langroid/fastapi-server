# Curl tests for local FastAPI endpoint served by Uvicorn/Docker

## Dummy test endpt

Local:

```bash
curl -X 'POST'\
  'http://localhost:80/test'\
  -H 'Content-Type: application/json'\
  -d '{"x": 10}'
```

Google cloud run (GCR): simply replace localhost endpt 
with the one from GCR, WITHOUT PORT NUMBER:

```bash
https://langroid-server-abcdefg-uk.a.run.app/test'\
```

```bash
curl -X 'POST'\
  'https://langroid-server-blahtal5mq-uk.a.run.app/test'\
  -H 'Content-Type: application/json'\
  -d '{"x": 10}'
```

## Agent Query endpoint

Local:

```bash
curl -X POST "http://localhost:80/agent/query" \
     -H "Content-Type: application/json" \
     -H "openai_api_key: sk..." \
     -d '{"query": "what is 10+20?"}'
```

