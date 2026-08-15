# Automated Google Cloud Run Deployment Script (PowerShell)
param (
    [string]$ProjectId = "",
    [string]$Region = "us-central1",
    [string]$ServiceName = "ai-strategic-advisor"
)

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " 🚀 Google Cloud Run Deployment: AI Strategic Advisor" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

# Check if gcloud is installed
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Google Cloud SDK ('gcloud') is not found in PATH." -ForegroundColor Red
    Write-Host "   Please install it using: winget install Google.CloudSDK" -ForegroundColor Yellow
    Write-Host "   Or run this from Google Cloud Shell in your browser." -ForegroundColor Yellow
    exit 1
}

# Prompt for Project ID if not supplied
if (-not $ProjectId) {
    $currentProject = (gcloud config get-value project 2>$null).Trim()
    if ($currentProject) {
        $ProjectId = $currentProject
        Write-Host "ℹ️ Using active GCP Project: $ProjectId" -ForegroundColor Green
    } else {
        $ProjectId = Read-Host "Enter your Google Cloud Project ID"
    }
}

if (-not $ProjectId) {
    Write-Host "❌ Project ID is required." -ForegroundColor Red
    exit 1
}

# Set project
Write-Host "`n[1/4] Setting active GCP Project..." -ForegroundColor Yellow
gcloud config set project $ProjectId

# Enable required Google Cloud APIs
Write-Host "`n[2/4] Enabling required GCP Services (Cloud Run, Cloud Build, Artifact Registry)..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

# Deploy directly via gcloud run deploy (source deployment automatically handles Docker build)
Write-Host "`n[3/4] Building container and deploying to Google Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --source . `
    --region $Region `
    --platform managed `
    --allow-unauthenticated `
    --port 8080 `
    --memory 2Gi `
    --cpu 2 `
    --set-env-vars "GEMINI_API_KEY=$($env:GEMINI_API_KEY)"

Write-Host "`n[4/4] Deployment Complete!" -ForegroundColor Green
Write-Host "Your AI Strategic Advisor is now live on Google Cloud Run!" -ForegroundColor Cyan
