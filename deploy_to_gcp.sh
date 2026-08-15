#!/bin/bash
# Automated Google Cloud Run Deployment Script (Bash / Cloud Shell)

set -e

PROJECT_ID=${1:-$(gcloud config get-value project 2>/dev/null)}
REGION="us-central1"
SERVICE_NAME="ai-strategic-advisor"

echo "========================================================="
echo " 🚀 Google Cloud Run Deployment: AI Strategic Advisor"
echo "========================================================="

if [ -z "$PROJECT_ID" ]; then
    read -p "Enter your Google Cloud Project ID: " PROJECT_ID
fi

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: Project ID is required."
    exit 1
fi

echo -e "\n[1/4] Setting active GCP Project to: $PROJECT_ID..."
gcloud config set project "$PROJECT_ID"

echo -e "\n[2/4] Enabling required GCP APIs..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

echo -e "\n[3/4] Building container and deploying to Google Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --region "$REGION" \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY}"

echo -e "\n[4/4] Deployment Complete! Check the URL above to access your live application."
