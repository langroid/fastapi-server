# Example FastAPI server using Langroid

### Setup
For env setup, follow the instructions
in the [langroid-examples](https://github.com/langroid/langroid-examples) repo, which 
means roughly the following. First ensure you have the latest `poetry` and 
you are using python 3.11+.

```bash
python3 -m venv .venv
. .venv/bin/activate
poetry env use 3.11
poetry install
```

Copy the `.env-template` to `.env` and fill in the values of the 
`OPENAI_API_KEY`, `QDRANT_API_KEY` and `QDRANT_API_URL` variables.
(The latter two are needed to use the [Qdrant Cloud](https://qdrant.tech/) vector-store;
consult their docs to see how to get these values.)


### Directory structure
Various files, dirs:

- `fastapi_server/`: FastAPI server code, defines the routes/endpoints. Contains:
    - `Dockerfile`: to build the docker container
    - `app.py`: defines the endpoints
    - `requirements.txt`: python dependencies
- `tests/`: tests for the FastAPI server
- `Makefile`: to build and run the docker container
- `server/`: auxiliary code modules that can be imported into `app.py`

### Building, running the docker container

```bash
make build
```

Note that this will run on `localhost:90` -- caution it's 90 not 80 
```bash
make up
```

See docker container logs in `tail -f` mode:

```bash
make tail
```

### Test the FastAPI server

This tests the server using both the test client provided by FastAPI
(which lets you step into the code while it's running),
and also the endpoint served via uvicorn from the docker container.

```bash
pytest -xs tests/test_fastapi.py
```




