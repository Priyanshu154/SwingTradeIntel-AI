# Frontend static site sync helper (fill bucket from `serverless info` output)
param(
  [Parameter(Mandatory = $true)][string]$BucketName,
  [string]$Profile = "swingtrade-deploy",
  [string]$DistPath = "dist"
)

if (-not (Test-Path $DistPath)) {
  Write-Error "Run npm run build first (missing $DistPath)"
  exit 1
}

aws s3 sync $DistPath "s3://$BucketName/" --delete --profile $Profile
Write-Host "Synced $DistPath -> s3://$BucketName/"
