.PHONY: build run test clean docker-build docker-run k8s-deploy terraform-init terraform-apply demo

# Go build
build:
	go mod tidy
	go build -o bin/opstool-server ./cmd/server

# Run locally
run:
	mkdir -p logs
	go run ./cmd/server

# Run tests
test:
	go test ./...

# Clean build artifacts
clean:
	rm -rf bin/

# Python setup
python-setup:
	cd scripts && pip install -r requirements.txt

# Start Python worker
python-worker:
	cd scripts && python worker.py

# Docker operations
docker-build:
	docker build -t opstool/server:latest .
	docker build -f deployments/docker/Dockerfile.python -t opstool/worker:latest .

docker-run:
	cd deployments/docker && docker-compose up -d

docker-stop:
	cd deployments/docker && docker-compose down

# Kubernetes operations
k8s-deploy:
	kubectl apply -f deployments/k8s/namespace.yaml
	kubectl apply -f deployments/k8s/redis.yaml
	kubectl apply -f deployments/k8s/postgres.yaml
	kubectl apply -f deployments/k8s/opstool-server.yaml
	kubectl apply -f deployments/k8s/opstool-worker.yaml

k8s-delete:
	kubectl delete -f deployments/k8s/

# Terraform operations
terraform-init:
	cd deployments/terraform && terraform init

terraform-plan:
	cd deployments/terraform && terraform plan

terraform-apply:
	cd deployments/terraform && terraform apply

terraform-destroy:
	cd deployments/terraform && terraform destroy

# Development
dev-setup: python-setup
	go mod download

dev-run: docker-run
	sleep 10
	make python-worker &
	make run

# Production deployment
prod-deploy: terraform-apply k8s-deploy

# Monitoring
logs-server:
	kubectl logs -f deployment/opstool-server -n opstool

logs-worker:
	kubectl logs -f deployment/opstool-worker -n opstool

# Health checks
health-check:
	curl -f http://localhost:8080/health || exit 1

# Demo and testing
startup-check:
	python scripts/startup_check.py

demo: startup-check
	python scripts/demo_usage.py

# Load testing
load-test:
	python scripts/load_test.py

# Security scanning
security-scan:
	python scripts/security_scanner.py

# Compliance check
compliance-check:
	python scripts/compliance_checker.py

# Backup operations
backup:
	python scripts/backup_automation.py

# Chaos engineering
chaos-test:
	python scripts/chaos_engineering.py

# Complete system verification
verify-all: startup-check demo load-test security-scan compliance-check
	@echo "🎉 All verification tests completed!"

# Go convenience checks
go-checks:
	go mod tidy
	go build ./...
	go test ./...

# Quick start for new users
quick-start:
	@echo "🚀 OPSTOOL Quick Start"
	@echo "1. Setting up dependencies..."
	make dev-setup
	@echo "2. Starting services..."
	make docker-run
	@echo "3. Waiting for services to be ready..."
	sleep 15
	@echo "4. Running startup verification..."
	make startup-check
	@echo "5. Running demo..."
	make demo
	@echo "✅ OPSTOOL is ready! Access dashboard at http://localhost:8080"

# Python checks
python-checks:
	cd scripts && python -m pytest
	cd scripts && ruff check .
	cd scripts && flake8 .