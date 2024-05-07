from fastapi import FastAPI, File, Header, UploadFile, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from tempfile import NamedTemporaryFile
import shutil
import hashlib
import json
from pydantic import BaseModel, Json
import uvicorn
import os
import openai
from time import time
import langroid as lr
import langroid.language_models as lm
from server.agents.rag_agent import RagAgentConfig, RagAgent
import logging

#TODO IMPORTANT - if we enable RAG, need to include `hf-embeddings` extra
# for langroid in requirements.txt

logger = logging.getLogger(__name__)

def check_openai_api_key(api_key):
    client = openai.OpenAI(api_key=api_key)
    try:
        client.models.list()
        openai.api_key = api_key
        os.environ["OPENAI_API_KEY"] = api_key
        return True
    except openai.AuthenticationError as e:
        return False


class Server:
    def __init__(self):
        self.setup()

    def setup(self):
        # Perform your potentially expensive initial setup here
        pass

    def ask_doc(self, doc_path: str, query: str) -> str:
        """Answer question `query` based on document at `doc_path`."""
        logger.warning(f"Getting full doc content from {doc_path} to make id")
        start = time()
        content = lr.parsing.utils.extract_content_from_path(
            doc_path, RagAgentConfig().parsing
        )
        logger.warning(f"Extracted content in {time()-start:.2f} seconds")

        if isinstance(content, list):
            content = " ".join(content)
        content = content[:500]
        id = hashlib.md5((doc_path + content).encode()).hexdigest()
        doc_id = f"langroid-rag-{id}"

        rag_config = RagAgentConfig(
            llm = lm.OpenAIGPTConfig(
                timeout=45,
                chat_model=lm.OpenAIChatModel.GPT4_TURBO,
            ),
        )
        if isinstance(rag_config.vecdb, lr.vector_store.QdrantDBConfig):
            rag_config.filter=json.dumps(
                {"must": [
                    {"key":"metadata.document", "match": {"value":doc_id}}
                ]
                }
            )
        elif isinstance(rag_config.vecdb, lr.vector_store.LanceDBConfig):
            rag_config.filter = f"metadata.document=='{doc_id}'"


        logger.warning(f"Initializating rag agent...")
        start = time()
        rag_agent = RagAgent(rag_config)
        logger.warning(f"Initialized rag agent in {time()-start:.2f} seconds")

        logger.warning(f"Ingesting doc {doc_path} into vector store...")
        start = time()
        rag_agent.ingest_doc_paths(
            [doc_path],
            metadata=lr.DocMetaData(document=doc_id),
        )
        logger.warning(f"Ingested doc in {time()-start:.2f} seconds")

        logger.warning(f"Answering query...")
        start = time()
        response = rag_agent.llm_response(query).content
        logger.warning(f"Answered query in {time()-start:.2f} seconds")
        return response

app = FastAPI()
server = Server()

@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    # Log the exception details or send them to an external monitoring service
    print(f"Unhandled exception: {exc}")
    # Return a generic response or customize based on exception details
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred"},
    )

class Item(BaseModel):
    x: int

class Query(BaseModel):
    query: str

@app.post("/test")
async def test(item: Item) -> int:
    return item.x * 5

@app.post("/agent/query")
async def agent_query(query: Query, openai_api_key: str = Header(...)) -> str:
    if not check_openai_api_key(openai_api_key):
        raise HTTPException(status_code=401, detail="Invalid OpenAI API key")
    try:
        agent = lr.ChatAgent()
        print(f"llm cfg api key = {agent.llm.config.api_key}")
        print(f"llm api key = {agent.llm.api_key}")
        print(f"openai.api_key: {openai.api_key}")
        print(f"env OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
        response = agent.llm_response(query.query).content
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent-ollama/query")
async def agent_ollama_query(query: Query) -> str:
    try:
        #os.environ["OLLAMA_HOST"]="0.0.0.0:11434"
        agent = lr.ChatAgent(
            lr.ChatAgentConfig(
                llm=lm.OpenAIGPTConfig(chat_model="ollama/llama2"),
            )
        )
        # import ollama
        # #verify llama2
        # ollama_show = ollama.show("llama2")
        # print(ollama_show)
        # assert ollama.show("llama2")["details"]["family"] == "llama"
        # logger.warning("ollama model verified")
        # import requests
        # import json
        #
        # url = 'http://localhost:11434/api/generate'
        # data = {
        #     "model": "llama2",
        #     "prompt": "What is 3+5?",
        #     "stream": False
        # }
        #
        # response = requests.post(url, json=data)
        # logger.warning(f"Test response: {response.json()}")
        logger.warning("Agent created properly, now getting response")
        response = agent.llm_response(query.query).content
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _copy_to_temp_file(file: UploadFile) -> NamedTemporaryFile:
    _, file_extension = os.path.splitext(file.filename)
    with NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file.flush()
        os.fsync(temp_file.fileno())
    return temp_file

@app.post("/langroid/askdoc")
async def ask_doc(
    doc: UploadFile = File(...),
    query: Json[Query] = Form(...),
    openai_api_key: str = Header(...),
) -> str:
    if not check_openai_api_key(openai_api_key):
        raise HTTPException(status_code=401, detail="Invalid OpenAI API key")
    temp_file = None
    try:
        temp_file = _copy_to_temp_file(doc)
        response = server.ask_doc(temp_file.name, query.query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file and os.path.exists(temp_file.name):
            os.remove(temp_file.name)



# This port number must match the port number in the Dockerfile
if __name__ == "__main__":
    # Use environment variables to control debug and reload options
    DEBUG = os.getenv("DEBUG", "false").lower() in ["true", "1", "t"]
    RELOAD = os.getenv("RELOAD", "false").lower() in ["true", "1", "t"]

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=90,
        # deubg=DEBUG,
        # reload=RELOAD,
        # log_level="debug" if DEBUG else "info",
    )
