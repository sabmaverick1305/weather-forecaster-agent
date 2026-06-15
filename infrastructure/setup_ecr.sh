#!/usr/bin/env bash
# Creates ECR repositories for all four services.
# Run once per AWS account/region.
set -euo pipefail

AWS_REGION="${AWS_REGION:-us-east-1}"
REPOS=(weather-mcp-server weather-agent weather-backend weather-frontend)

for repo in "${REPOS[@]}"; do
  echo "Creating ECR repository: $repo"
  aws ecr create-repository \
    --repository-name "$repo" \
    --region "$AWS_REGION" \
    --image-scanning-configuration scanOnPush=true \
    --image-tag-mutability MUTABLE \
    --output json | jq -r '.repository.repositoryUri'
done

echo "Done. Add the repository URIs to your .env and GitHub Secrets."
