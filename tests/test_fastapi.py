import pytest
from typing import Any, Tuple
from fastapi.testclient import TestClient
from fastapi_server.app import app, Query
import mimetypes
import requests
from dotenv import load_dotenv
import os
import json
import logging

logger = logging.getLogger(__name__)
load_dotenv()

def get_content_type(filename: str) -> str:
    """
    Returns the MIME type for the given filename based on its extension.
    """
    mimetype, _ = mimetypes.guess_type(filename)
    return mimetype or 'application/octet-stream'  # Default to 'application/octet-stream' if the MIME type is not found

def get_url_client(route:str, real: bool) -> Tuple[str, Any]:
    if real:
        base_url = os.getenv("LANGROID_BASE_URL", "http://localhost:90")
        url = f"{base_url}{route}"
        client = requests
    else:
        url = route
        client = TestClient(app)
    return url, client

@pytest.mark.parametrize("real_endpoint", [True, False])
def test_agent_query(real_endpoint:bool):
    url, client = get_url_client(route = "/agent/query", real = real_endpoint)

    headers = {
        "openai-api-key": os.getenv("OPENAI_API_KEY")
    }
    response = client.post(
        url,
        json={"query": "What is 3+4?"},
        headers=headers
    )
    assert response.status_code == 200
    assert "7" in response.json()

@pytest.mark.parametrize("real_endpoint", [False,True])
def test_agent_ollama_query(real_endpoint:bool):
    url, client = get_url_client(route = "/agent-ollama/query", real = real_endpoint)

    response = client.post(
        url,
        json={"query": "What is 3+4?"},
    )
    assert response.status_code == 200
    assert "7" in response.json()

@pytest.mark.parametrize("real_endpoint", [True, False])
def test_toy_endpoint(real_endpoint:bool):
    url, client = get_url_client(route = "/test", real = real_endpoint)
    response = client.post(url, json={"x": 10})
    assert response.status_code == 200
    assert response.json() == 50

@pytest.mark.parametrize(
    "doc",
    ["tests/data/moon-pilot-req.txt", "tests/data/mobile-job-desc.pdf"]
)
@pytest.mark.parametrize("real_endpoint", [False,True])
def test_ask_doc(doc, real_endpoint:bool):
    real_str = "CONTAINER ENDPT" if real_endpoint else "CODE"
    logger.warning(f"\n\n****** TESTING against {real_str} with file {doc} ******\n\n")
    logger.warning(f"------------------------------------")
    url, client = get_url_client(route = "/langroid/askdoc", real = real_endpoint)
    headers = {
        "openai-api-key": os.getenv("OPENAI_API_KEY")
    }
    query = "What is the job description about, in one short sentence?"

    with open(doc, 'rb') as f:
        files = {
            'doc': f
        }
        response = client.post(
            url,
            data={"query": Query(query=query).json()},
            files=files,
            headers=headers
        )

    assert response.status_code == 200
    assert "job" in response.json()

