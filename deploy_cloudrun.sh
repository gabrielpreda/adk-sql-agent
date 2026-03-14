#!/bin/bash

# ADK SQL Agent - Cloud Run Deployment Script
# Alternative deployment using Google Cloud Run

set -e

# Configuration
PROJECT_ID="your-project"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
SERVICE_NAME="adk-sql-agent"

REPO_LOCATION="us"  # same as you used when creating the repo
REPO_NAME="adk-sql-agent-repo"
IMAGE_NAME="${REPO_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}"
#IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Deploying ADK SQL Agent to Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Step 1: Enable required APIs
echo "📦 Enabling required APIs..."
~/google-cloud-sdk/bin/gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  aiplatform.googleapis.com \
  --project=$PROJECT_ID

# Step 2: Build the container image
echo "🏗️  Building container image..."
~/google-cloud-sdk/bin/gcloud builds submit \
  --tag $IMAGE_NAME \
  --project=$PROJECT_ID

# Step 3: Deploy to Cloud Run
echo "🚢 Deploying to Cloud Run..."
~/google-cloud-sdk/bin/gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_GENAI_USE_VERTEXAI=TRUE \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
  --set-env-vars GOOGLE_CLOUD_LOCATION=$REGION \
  --memory 4Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10 \
  --timeout 300 \
  --project=$PROJECT_ID

# Get the service URL
SERVICE_URL=$(~/google-cloud-sdk/bin/gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --project=$PROJECT_ID \
  --format='value(status.url)')

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Service URL: $SERVICE_URL"
echo ""
echo "To test your service:"
echo "  curl $SERVICE_URL/status"
echo ""
echo "To send a query:"
echo "  curl -X POST $SERVICE_URL/query \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"query\": \"Show me the top 10 authors by sales\"}'"
echo ""
echo "To view logs:"
echo "gcloud run services logs read $SERVICE_NAME --project=$PROJECT_ID --region=$REGION"