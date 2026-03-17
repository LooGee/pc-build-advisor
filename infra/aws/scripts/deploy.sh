#!/bin/bash
set -e

ENVIRONMENT=${1:-staging}
VERSION=${2:-$(git rev-parse --short HEAD)}
AWS_REGION=${AWS_REGION:-ap-northeast-2}

echo "Deploying PC Build Advisor to $ENVIRONMENT (version: $VERSION)"

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $ECR_REGISTRY

# Build and push images
for SERVICE in backend frontend ai-service crawler; do
  echo "Building $SERVICE..."
  docker build -t $ECR_REGISTRY/pc-advisor-$SERVICE:$VERSION ./$SERVICE
  docker push $ECR_REGISTRY/pc-advisor-$SERVICE:$VERSION
done

# Update ECS services
CLUSTER="pc-advisor-$ENVIRONMENT"
for SERVICE in backend frontend ai-service crawler; do
  echo "Deploying $SERVICE to ECS..."
  aws ecs update-service \
    --cluster $CLUSTER \
    --service $SERVICE \
    --force-new-deployment \
    --region $AWS_REGION
done

echo "Deployment complete!"
echo "Monitor: https://console.aws.amazon.com/ecs/clusters/$CLUSTER/services"
