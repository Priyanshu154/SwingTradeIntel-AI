# Infrastructure

IaC for this project lives next to the Lambda code:

- [`backend/serverless.yml`](../backend/serverless.yml) — Serverless Framework v3
  - API Gateway HTTP API
  - 7 Lambdas (orchestrator, history, 3 agents, judge, weekly ingest)
  - DynamoDB `AnalysisCache` + `ChatSessions`
  - S3 news corpus + frontend static website bucket
  - EventBridge Scheduler (Sunday cron)

Deploy credentials are loaded from SSM (`/IAM_ACCESS_KEY`, `/IAM_SECRET_ACCESS`) into a local AWS CLI profile via [`scripts/setup-deploy-profile.ps1`](../scripts/setup-deploy-profile.ps1) — never injected into Lambda runtime env.
