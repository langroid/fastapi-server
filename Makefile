# Makefile for managing Docker operations

# export all vars so docker-compose can use them
export
# Dynamically find the most recently run container and its image
# CURRENT_CONTAINER := $(shell docker ps -l -q)
# CURRENT_IMAGE := $(shell docker inspect --format='{{.Config.Image}}' $(CURRENT_CONTAINER))

# Customize these variables for your project
LOCAL_ARCH := $(shell uname -m)
GCLOUD_ARCH := amd64
IMAGE_NAME := langroid-fastapi-server
G_IMAGE_NAME := langroid-fastapi-server
# Use CURRENT_IMAGE if available, otherwise fallback to a default

CONTAINER_NAME := langroid-container

GCLOUD_PROJECT_ID := langroid
GCLOUD_REGISTRY_PREFIX := gcr.io
GCLOUD_IMAGE_NAME := $(GCLOUD_REGISTRY_PREFIX)/$(GCLOUD_PROJECT_ID)/$(G_IMAGE_NAME)

GCLOUD_RUN_SERVICE := langroid-server
GCLOUD_REGION := us-east4
BUCKET_NAME := fastapi-server-$(GCLOUD_PROJECT_ID)

DOCKERFILE_PATH := fastapi_server/Dockerfile

REGION := us-east4
PORT := 90
TAG := latest

clear:
	# @echo "Removing all Docker containers..."
	# @docker rm -f $(docker ps -aq) || true
	# @echo "Removing all Docker images..."
	# @docker rmi -f $(docker images -a -q) || true
	# @echo "pruning all Docker volumes..."
	# @docker container prune -f
	# @echo "pruning all Docker networks..."
	# @docker network prune -f
	# @echo "pruning system..."
	# @docker system prune -f
	@echo "Removing unused volumes..."
	@docker volume prune -f
	@echo "Removing unused networks..."
	@docker network prune -f
	@echo "Docker clean up complete."
# use
build:
	docker-compose build

rbuild:
	docker-compose build --no-cache

up:
	export DEBUG=False RELOAD=true; \
	docker-compose up -d

down:
	docker-compose down

debug:
	@docker logs $$(docker ps -a -q -l)

tail:
	docker-compose logs -f

server:
	docker build --platform linux/$(LOCAL_ARCH) -t $(IMAGE_NAME):$(TAG) -f $(DOCKERFILE_PATH) .

run:
	docker run --env-file .env -d -p $(PORT):$(PORT) $(IMAGE_NAME):$(TAG)

# Stop the Docker container
stop:
	docker stop $(CONTAINER_NAME)
	docker rm $(CONTAINER_NAME)

stats:
	docker stats $(CONTAINER_NAME)
# Shortcut to stop (if running) and then start the container
restart: stop run

# Start a shell session in a new container from the image
sh:
	@docker exec -it $$(docker ps -q | head -n1) sh

# Start a Python console in a new container from the image
py:
	docker run -it --rm --name $(CONTAINER_NAME)_python $(IMAGE_NAME) python

glist-cont-imgs:
	gcloud container images list --repository=$(GCLOUD_IMAGE_NAME)

gserver:
	export DEBUG=false RELOAD=false; \
	docker build --platform=linux/$(GCLOUD_ARCH) -t $(GCLOUD_IMAGE_NAME):$(TAG) -f $(DOCKERFILE_PATH) .

gpush:
	docker push $(GCLOUD_IMAGE_NAME):$(TAG)

gdeploy:
	gcloud run deploy $(GCLOUD_RUN_SERVICE) --image $(GCLOUD_IMAGE_NAME):$(TAG) \
			--platform managed --region $(GCLOUD_REGION) \
			--project $(GCLOUD_PROJECT_ID) --allow-unauthenticated \
			--timeout 1000s --port $(PORT) --memory 32Gi --cpu 8

gtail:
	gcloud beta logging tail
		--log-filter="resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"$(GCLOUD_RUN_SERVICE)\""
		--project=$(GCLOUD_PROJECT_ID)

gbucket:
	gsutil mb -p $(GCLOUD_PROJECT_ID) -c standard -l $(GCLOUD_REGION) -b on gs://$(BUCKET_NAME)/

gsh:
	docker run -it --entrypoint /bin/sh $(GCLOUD_IMAGE_NAME):$(TAG)

gstop:
	gcloud run services update $(GCLOUD_RUN_SERVICE) --region=(GCLOUD_REGION) --no-traffic

# Help
help:
	@echo "Makefile commands:"
	@echo "server   - Build the server, i.e. Docker image."
	@echo "run      - Run the Docker container."
	@echo "stop     - Stop and remove the Docker container."
	@echo "restart  - Restart the Docker container."
	@echo "help     - Print this help message."
	@echo "gserver  - Build the server for Google Cloud."
	@echo "gpush    - Push the server to Google Cloud."
	@echo "sh       - Start a shell session in a new container from the image."
	@echo "py       - Start a Python console in a new container from the image."



.PHONY: server run stop restart help gbucket