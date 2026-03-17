#!/bin/bash
set -e

ENVIRONMENT=${1:-staging}
PREVIOUS_VERSION=${2}

if [ -z "$PREVIOUS_VERSION" ]; then
  echo "Usage: $0 <environment> <previous-version>"
  exit 1
fi

echo "Rolling back to version $PREVIOUS_VERSION in $ENVIRONMENT"

CLUSTER="pc-advisor-$ENVIRONMENT"
AWS_REGION=${AWS_REGION:-ap-northeast-2}

for SERVICE in backend frontend ai-service crawler; do
  # Get current task definition
  TASK_DEF=$(aws ecs describe-services \
    --cluster $CLUSTER \
    --services $SERVICE \
    --query 'services[0].taskDefinition' \
    --output text \
    --region $AWS_REGION)

  # Register new task definition with previous image
  echo "Rolling back $SERVICE..."
  aws ecs update-service \
    --cluster $CLUSTER \
    --service $SERVICE \
    --task-definition $TASK_DEF \
    --force-new-deployment \
    --region $AWS_REGION
done

echo "Rollback initiated. Monitor ECS console for progress."
