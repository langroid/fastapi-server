FROM python:3.11


# Set the working directory in the container
WORKDIR /app

COPY server/ /app/server/

COPY fastapi_server/ /app/fastapi_server/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/fastapi_server/requirements.txt

# libmagic to detect file type in the unstructured lib
RUN apt-get update && \
    apt-get install -y libmagic-dev libreoffice && \
    rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

RUN python -m compileall .

# port
EXPOSE 90

CMD ollama run llama2 & uvicorn fastapi_server.app:app --host 0.0.0.0 --port 90 --workers 4

# Command to run the application
# CMD ["uvicorn", "fastapi_server.app:app", "--host", "0.0.0.0", "--port", "90", "--workers", "4"]
