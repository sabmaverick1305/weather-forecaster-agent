#!/usr/bin/env python3
"""
Creates or updates the AWS Bedrock AgentCore Runtime.

Usage:
  # Create (first time):
  python create_agentcore_runtime.py --image 123456789012.dkr.ecr.us-east-1.amazonaws.com/weather-agent:latest

  # Update image on existing runtime:
  python create_agentcore_runtime.py --image <uri> --agent-runtime-arn <arn>
"""
import argparse
import os
import boto3

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
ACCOUNT_ID = boto3.client("sts", region_name=AWS_REGION).get_caller_identity()["Account"]
EXECUTION_ROLE_ARN = os.environ.get(
    "AGENTCORE_EXECUTION_ROLE_ARN",
    f"arn:aws:iam::{ACCOUNT_ID}:role/weather-agentcore-runtime-role",
)

ENV_VARS = {
    "MCP_SERVER_URL": os.environ.get("MCP_SERVER_URL", ""),
    "BEDROCK_MODEL_ID": os.environ.get("BEDROCK_MODEL_ID", "us.amazon.nova-lite-v1:0"),
    "AWS_REGION": AWS_REGION,
}


def create_runtime(client, image_uri: str) -> str:
    response = client.create_agent_runtime(
        agentRuntimeName="weather_forecast_agent",
        description="Weather forecast AI agent Amazon Nova Lite MCP tools OpenWeatherMap",
        agentRuntimeArtifact={
            "containerConfiguration": {
                "containerUri": image_uri,
            }
        },
        networkConfiguration={"networkMode": "PUBLIC"},
        roleArn=EXECUTION_ROLE_ARN,
        environmentVariables={k: v for k, v in ENV_VARS.items() if v},
    )
    arn = response["agentRuntimeArn"]
    print(f"Created AgentCore Runtime: {arn}")
    return arn


def update_runtime(client, arn: str, image_uri: str) -> None:
    client.update_agent_runtime(
        agentRuntimeId=arn.split("/")[-1],
        agentRuntimeArtifact={
            "containerConfiguration": {
                "containerUri": image_uri,
            }
        },
        networkConfiguration={"networkMode": "PUBLIC"},
        roleArn=EXECUTION_ROLE_ARN,
        environmentVariables={k: v for k, v in ENV_VARS.items() if v},
    )
    print(f"Updated AgentCore Runtime: {arn}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Full ECR image URI including tag")
    parser.add_argument("--agent-runtime-arn", default="", help="Existing runtime ARN (omit to create new)")
    args = parser.parse_args()

    client = boto3.client("bedrock-agentcore-control", region_name=AWS_REGION)

    if args.agent_runtime_arn:
        update_runtime(client, args.agent_runtime_arn, args.image)
        arn = args.agent_runtime_arn
    else:
        arn = create_runtime(client, args.image)

    print("\nSave this ARN as AGENT_RUNTIME_ARN in GitHub Secrets and .env:")
    print(arn)


if __name__ == "__main__":
    main()
