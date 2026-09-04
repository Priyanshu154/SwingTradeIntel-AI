#!/usr/bin/env bash
# Configure a local AWS CLI profile from SSM deploy credentials.
# These keys are for deploy-time only — never bake them into Lambda env.
set -euo pipefail

REGION="${AWS_REGION:-us-east-1}"
PROFILE="${AWS_PROFILE_NAME:-swingtrade-deploy}"

ACCESS_KEY=$(aws ssm get-parameter \
  --name /IAM_ACCESS_KEY \
  --with-decryption \
  --region "$REGION" \
  --query Parameter.Value \
  --output text)

SECRET_KEY=$(aws ssm get-parameter \
  --name /IAM_SECRET_ACCESS \
  --with-decryption \
  --region "$REGION" \
  --query Parameter.Value \
  --output text)

aws configure set aws_access_key_id "$ACCESS_KEY" --profile "$PROFILE"
aws configure set aws_secret_access_key "$SECRET_KEY" --profile "$PROFILE"
aws configure set region "$REGION" --profile "$PROFILE"

echo "Configured AWS profile: $PROFILE (region $REGION)"
echo "Deploy with: cd backend && AWS_PROFILE=$PROFILE npm run deploy"
