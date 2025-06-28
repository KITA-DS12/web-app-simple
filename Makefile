.PHONY: dev test build push deploy clean

# Variables
IMAGE ?= gcr.io/my-project/fastapi-react-app
SERVICE ?= fastapi-react-app
REGION ?= us-central1

# Development
dev:
	cd infra && docker-compose up --build

dev-down:
	cd infra && docker-compose down -v

# Testing
test:
	cd server && pytest -q

test-verbose:
	cd server && pytest -v

# Build
build:
	docker build -t $(IMAGE) -f infra/Dockerfile .

# Push to registry
push: build
	docker push $(IMAGE)

# Deploy to Cloud Run
deploy:
	bash infra/deploy.sh $(IMAGE) $(SERVICE) $(REGION)

# Full deployment pipeline
deploy-all: build push deploy

# Clean up
clean:
	cd infra && docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf server/.pytest_cache
	rm -rf client/node_modules client/dist

# Database migrations (placeholder)
migrate:
	@echo "Alembic migrations not implemented yet"

# Help
help:
	@echo "Available commands:"
	@echo "  make dev          - Start development environment"
	@echo "  make dev-down     - Stop development environment"
	@echo "  make test         - Run tests"
	@echo "  make build        - Build Docker image"
	@echo "  make push         - Push image to registry"
	@echo "  make deploy       - Deploy to Cloud Run"
	@echo "  make deploy-all   - Build, push and deploy"
	@echo "  make clean        - Clean up generated files"