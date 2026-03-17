.PHONY: build push deploy rollback

ECR_REGISTRY ?= $(shell aws ecr describe-repositories --query 'repositories[0].repositoryUri' --output text | cut -d'/' -f1)
VERSION ?= $(shell git rev-parse --short HEAD)
CLUSTER ?= pc-advisor-prod

build:
	docker build -t $(ECR_REGISTRY)/pc-advisor-backend:$(VERSION) ../../backend
	docker build -t $(ECR_REGISTRY)/pc-advisor-frontend:$(VERSION) ../../frontend
	docker build -t $(ECR_REGISTRY)/pc-advisor-ai-service:$(VERSION) ../../ai-service
	docker build -t $(ECR_REGISTRY)/pc-advisor-crawler:$(VERSION) ../../crawler-service

push: build
	aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin $(ECR_REGISTRY)
	docker push $(ECR_REGISTRY)/pc-advisor-backend:$(VERSION)
	docker push $(ECR_REGISTRY)/pc-advisor-frontend:$(VERSION)
	docker push $(ECR_REGISTRY)/pc-advisor-ai-service:$(VERSION)
	docker push $(ECR_REGISTRY)/pc-advisor-crawler:$(VERSION)

deploy: push
	aws ecs update-service --cluster $(CLUSTER) --service backend --force-new-deployment
	aws ecs update-service --cluster $(CLUSTER) --service frontend --force-new-deployment
	aws ecs update-service --cluster $(CLUSTER) --service ai-service --force-new-deployment
	aws ecs update-service --cluster $(CLUSTER) --service crawler --force-new-deployment

seed-db:
	aws ecs run-task --cluster $(CLUSTER) --task-definition pc-advisor-seed --launch-type FARGATE
