#!/usr/bin/env bash
# Creates IAM roles required for ECS tasks and AgentCore Runtime.
# Run once. Requires admin or IAM permissions.
set -euo pipefail

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION="${AWS_REGION:-us-east-1}"

echo "Account: $AWS_ACCOUNT_ID  Region: $AWS_REGION"

# ── 1. ECS Task Execution Role ───────────────────────────────────────────────
aws iam create-role \
  --role-name weather-ecs-task-execution-role \
  --assume-role-policy-document '{
    "Version":"2012-10-17",
    "Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]
  }' --output json | jq -r '.Role.Arn'

aws iam attach-role-policy \
  --role-name weather-ecs-task-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Allow reading Secrets Manager for OWM_API_KEY
aws iam put-role-policy \
  --role-name weather-ecs-task-execution-role \
  --policy-name secrets-read \
  --policy-document "{
    \"Version\":\"2012-10-17\",
    \"Statement\":[{
      \"Effect\":\"Allow\",
      \"Action\":[\"secretsmanager:GetSecretValue\",\"kms:Decrypt\"],
      \"Resource\":\"arn:aws:secretsmanager:${AWS_REGION}:${AWS_ACCOUNT_ID}:secret:/weather-agent/*\"
    }]
  }"

echo "Created: weather-ecs-task-execution-role"

# ── 2. ECS Task Role (assumed by running containers) ─────────────────────────
aws iam create-role \
  --role-name weather-ecs-task-role \
  --assume-role-policy-document '{
    "Version":"2012-10-17",
    "Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]
  }' --output json | jq -r '.Role.Arn'

aws iam put-role-policy \
  --role-name weather-ecs-task-role \
  --policy-name bedrock-invoke \
  --policy-document "{
    \"Version\":\"2012-10-17\",
    \"Statement\":[
      {
        \"Effect\":\"Allow\",
        \"Action\":[\"bedrock-agentcore:InvokeAgentRuntime\",\"bedrock:InvokeModel\"],
        \"Resource\":\"*\"
      },
      {
        \"Effect\":\"Allow\",
        \"Action\":[\"logs:CreateLogGroup\",\"logs:CreateLogStream\",\"logs:PutLogEvents\"],
        \"Resource\":\"*\"
      }
    ]
  }"

echo "Created: weather-ecs-task-role"

# ── 3. AgentCore Runtime Role ─────────────────────────────────────────────────
aws iam create-role \
  --role-name weather-agentcore-runtime-role \
  --assume-role-policy-document '{
    "Version":"2012-10-17",
    "Statement":[{"Effect":"Allow","Principal":{"Service":"bedrock-agentcore.amazonaws.com"},"Action":"sts:AssumeRole"}]
  }' --output json | jq -r '.Role.Arn'

aws iam put-role-policy \
  --role-name weather-agentcore-runtime-role \
  --policy-name bedrock-model \
  --policy-document '{
    "Version":"2012-10-17",
    "Statement":[{
      "Effect":"Allow",
      "Action":["bedrock:InvokeModel","bedrock:InvokeModelWithResponseStream"],
      "Resource":[
        "arn:aws:bedrock:*::foundation-model/anthropic.*",
        "arn:aws:bedrock:*::foundation-model/amazon.*",
        "arn:aws:bedrock:*:*:inference-profile/us.amazon.*",
        "arn:aws:bedrock:*:*:inference-profile/global.amazon.*"
      ]
    }]
  }'

echo "Created: weather-agentcore-runtime-role"
echo ""
echo "Role ARNs:"
aws iam get-role --role-name weather-ecs-task-execution-role --query 'Role.Arn' --output text
aws iam get-role --role-name weather-ecs-task-role --query 'Role.Arn' --output text
aws iam get-role --role-name weather-agentcore-runtime-role --query 'Role.Arn' --output text
