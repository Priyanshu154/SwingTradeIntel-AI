# Configure a local AWS CLI profile from SSM deploy credentials (Windows PowerShell).
# Deploy-time only — never put these keys in Lambda environment variables.
param(
  [string]$Region = "us-east-1",
  [string]$Profile = "swingtrade-deploy"
)

$accessKey = aws ssm get-parameter --name /IAM_ACCESS_KEY --with-decryption --region $Region --query Parameter.Value --output text
$secretKey = aws ssm get-parameter --name /IAM_SECRET_ACCESS --with-decryption --region $Region --query Parameter.Value --output text

aws configure set aws_access_key_id $accessKey --profile $Profile
aws configure set aws_secret_access_key $secretKey --profile $Profile
aws configure set region $Region --profile $Profile

Write-Host "Configured AWS profile: $Profile (region $Region)"
Write-Host "Deploy with: cd backend; `$env:AWS_PROFILE='$Profile'; npm run deploy"
