# Quick Deployment Reference

## Setup
```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
```

## Agent Engine Deployment

### Deploy
```bash
./deploy.sh
```

### Test
```bash
adk run --project=$GOOGLE_CLOUD_PROJECT --region=$GOOGLE_CLOUD_LOCATION --agent=adk-sql-agent
```

### Manage
```bash
# List agents
adk list --project=$GOOGLE_CLOUD_PROJECT --region=$GOOGLE_CLOUD_LOCATION

# Describe agent
adk describe --project=$GOOGLE_CLOUD_PROJECT --region=$GOOGLE_CLOUD_LOCATION --agent=adk-sql-agent

# Update agent
adk deploy --project=$GOOGLE_CLOUD_PROJECT --region=$GOOGLE_CLOUD_LOCATION --agent-config=agent_engine.yaml

# Delete agent
adk delete --project=$GOOGLE_CLOUD_PROJECT --region=$GOOGLE_CLOUD_LOCATION --agent=adk-sql-agent
```

## Cloud Run Deployment

### Deploy
```bash
./deploy_cloudrun.sh
```

### Test
```bash
# Get URL
SERVICE_URL=$(gcloud run services describe adk-sql-agent --platform managed --region $GOOGLE_CLOUD_LOCATION --format='value(status.url)')

# Health check
curl $SERVICE_URL/status

# Query
curl -X POST $SERVICE_URL/query \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me the top 10 customers"}'
```

### Manage
```bash
# View logs
gcloud run services logs read adk-sql-agent --region=$GOOGLE_CLOUD_LOCATION --limit=50

# Update resources
gcloud run services update adk-sql-agent --region=$GOOGLE_CLOUD_LOCATION --memory 8Gi

# Scale
gcloud run services update adk-sql-agent --region=$GOOGLE_CLOUD_LOCATION --min-instances 2 --max-instances 20

# Delete
gcloud run services delete adk-sql-agent --region=$GOOGLE_CLOUD_LOCATION
```

## Local Testing

### Run locally
```bash
# Start backend
uvicorn main:app --reload --port 8080

# Start frontend (in another terminal)
streamlit run streamlit_ui.py
```

### Test with ADK Web
```bash
adk web
# Then select the sql_agent folder
```

## Docker Testing

### Build
```bash
docker build -t adk-sql-agent .
```

### Run
```bash
docker run -p 8080:8080 \
  -e GOOGLE_GENAI_USE_VERTEXAI=TRUE \
  -e GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT \
  -e GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION \
  adk-sql-agent
```

### Test
```bash
curl http://localhost:8080/status
```
