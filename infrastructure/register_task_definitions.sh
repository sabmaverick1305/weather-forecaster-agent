#!/usr/bin/env bash
# Registers ECS task definitions and creates cluster + services.
# Run after setup_ecr.sh and setup_iam.sh.
# Requires: AWS_ACCOUNT_ID, AWS_REGION, AGENT_RUNTIME_ARN env vars.
set -euo pipefail

AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:?Set AWS_ACCOUNT_ID}"
AWS_REGION="${AWS_REGION:-us-east-1}"
AGENT_RUNTIME_ARN="${AGENT_RUNTIME_ARN:?Set AGENT_RUNTIME_ARN}"
CLUSTER="weather-agent-cluster"

# Substitute placeholders in task defs
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

substitute() {
  local file="$1"
  sed \
    -e "s/ACCOUNT_ID/${AWS_ACCOUNT_ID}/g" \
    -e "s/REGION/${AWS_REGION}/g" \
    -e "s|AGENT_RUNTIME_ARN_PLACEHOLDER|${AGENT_RUNTIME_ARN}|g" \
    "$file"
}

# Register task definitions
echo "Registering task definitions..."
substitute "$SCRIPT_DIR/task-def-mcp.json" | aws ecs register-task-definition --cli-input-json file:///dev/stdin --region "$AWS_REGION" --query 'taskDefinition.taskDefinitionArn' --output text
substitute "$SCRIPT_DIR/task-def-backend.json" | aws ecs register-task-definition --cli-input-json file:///dev/stdin --region "$AWS_REGION" --query 'taskDefinition.taskDefinitionArn' --output text
substitute "$SCRIPT_DIR/task-def-frontend.json" | aws ecs register-task-definition --cli-input-json file:///dev/stdin --region "$AWS_REGION" --query 'taskDefinition.taskDefinitionArn' --output text

# Create ECS cluster
echo "Creating ECS cluster: $CLUSTER"
aws ecs create-cluster --cluster-name "$CLUSTER" --region "$AWS_REGION" --output json | jq -r '.cluster.clusterArn'

# Create CloudWatch Log Groups
for svc in weather-mcp weather-backend weather-frontend; do
  aws logs create-log-group --log-group-name "/ecs/${svc}" --region "$AWS_REGION" 2>/dev/null || true
done

echo ""
echo "Task definitions registered and cluster created."
echo "Next steps:"
echo "  1. Note your VPC subnet IDs and security group IDs"
echo "  2. Create ECS services using the AWS Console or CLI with awsvpc networking"
echo "  3. Create an ALB routing /api/* to backend:8001 and /* to frontend:80"
