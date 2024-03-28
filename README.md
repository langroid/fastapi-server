# Example FastAPI server using Langroid
For env setup, follow the instructions
in the [langroid-examples](https://github.com/langroid/langroid-examples) repo.

Various files, dirs:

- `fastapi_server/`: FastAPI server code, defines the routes/endpoints. Contains:
    - `Dockerfile`: to build the docker container
    - `app.py`: defines the endpoints
    - `requirements.txt`: python dependencies
- `tests/`: tests for the FastAPI server
- `Makefile`: to build and run the docker container
- `server/`: auxiliary code modules that can be imported into `app.py`

# Build docker container

```bash
make build
```

# Run docker container

Note that this will run on `localhost:90` -- caution it's 90 not 80 
```bash
make up
```

# Test the FastAPI server

This tests the server using both the test client provided by FastAPI
(which lets you step into the code while it's running),
and also the endpoint served via uvicorn from the docker container.

```bash
pytest -xs tests/test_fastapi.py
```




