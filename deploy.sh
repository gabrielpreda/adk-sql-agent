#!/bin/bash

# ADK SQL Agent - Agent Engine Deployment Script
# This script deploys the ADK SQL Agent to Google Cloud Agent Engine

set -e

# Configuration
PROJECT_ID="gemini-first-439812"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
AGENT_NAME="adk-sql-agent"
SERVICE_ACCOUNT="${AGENT_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com"
AGENT_FOLDER="sql_agent"

echo "🚀 Deploying ADK SQL Agent to Agent Engine"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Step 1: Enable required APIs
echo "📦 Enabling required APIs..."
~/google-cloud-sdk/bin/gcloud services enable \
  aiplatform.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  --project=$PROJECT_ID

# Step 2: Create service account (if it doesn't exist)
echo "🔐 Setting up service account..."
if ! ~/google-cloud-sdk/bin/gcloud iam service-accounts describe $SERVICE_ACCOUNT --project=$PROJECT_ID &>/dev/null; then
  ~/google-cloud-sdk/bin/gcloud iam service-accounts create ${AGENT_NAME}-sa \
    --display-name="ADK SQL Agent Service Account" \
    --project=$PROJECT_ID
fi

# Step 3: Grant necessary permissions
echo "🔑 Granting permissions..."
~/google-cloud-sdk/bin/gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"

~/google-cloud-sdk/bin/gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/logging.logWriter"

# Step 4: Build and deploy using ADK CLI
echo "🏗️  Building and deploying agent..."
adk deploy agent_engine \
  --project=$PROJECT_ID \
  --region=$REGION \
  --agent_engine_config_file=agent_engine.yaml \
  $AGENT_FOLDER


echo "✅ Deployment complete!"
echo ""
echo "To test your deployed agent:"
echo "  adk run --project=$PROJECT_ID --region=$REGION --agent=$AGENT_NAME"
echo ""
echo "To view logs:"
echo "  gcloud logging read \"resource.type=cloud_run_revision\" --project=$PROJECT_ID --limit=50"
