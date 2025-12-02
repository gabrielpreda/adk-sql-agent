# Deployment Guide for ADK SQL Agent

This guide provides detailed instructions for deploying the ADK SQL Agent to Google Cloud.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Agent Engine Deployment](#agent-engine-deployment)
3. [Cloud Run Deployment](#cloud-run-deployment)
4. [Configuration](#configuration)
5. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)

## Prerequisites

### Required Tools
- **gcloud CLI**: [Install gcloud](https://cloud.google.com/sdk/docs/install)
- **ADK CLI**: Install with `pip install google-adk`
- **Docker** (optional): For local testing

### Google Cloud Setup
1. Create a Google Cloud Project
2. Enable billing for the project
3. Authenticate with gcloud:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

## Agent Engine Deployment

Agent Engine is the recommended deployment method for ADK agents.

### What is Agent Engine?

Agent Engine is a fully managed service that:
- Automatically scales your agent based on demand
- Handles infrastructure management
- Provides built-in monitoring and logging
- Integrates seamlessly with Vertex AI

### Deployment Steps

1. **Set Environment Variables**
   ```bash
   export GOOGLE_CLOUD_PROJECT=your-project-id
   export GOOGLE_CLOUD_LOCATION=us-central1
   ```

2. **Review Configuration**
   
   The `agent_engine.yaml` file contains your deployment configuration:
   - Agent entry point: `sql_agent.agent.root_agent`
   - Python version: 3.11
   - Resources: 2 CPU, 4Gi memory
   - Scaling: 1-10 instances

3. **Deploy**
   ```bash
   ./deploy.sh
   ```

   This script will:
   - Enable required Google Cloud APIs
   - Create a service account with necessary permissions
   - Build and deploy your agent
   - Configure auto-scaling

4. **Test the Deployment**
   ```bash
   adk run --project=$GOOGLE_CLOUD_PROJECT \
           --region=$GOOGLE_CLOUD_LOCATION \
           --agent=adk-sql-agent
   ```

### Agent Engine Commands

```bash
# List deployed agents
adk list --project=$GOOGLE_CLOUD_PROJECT --region=$GOOGLE_CLOUD_LOCATION

# Get agent details
adk describe --project=$GOOGLE_CLOUD_PROJECT \
             --region=$GOOGLE_CLOUD_LOCATION \
             --agent=adk-sql-agent

# Update agent
adk deploy --project=$GOOGLE_CLOUD_PROJECT \
           --region=$GOOGLE_CLOUD_LOCATION \
           --agent-config=agent_engine.yaml

# Delete agent
adk delete --project=$GOOGLE_CLOUD_PROJECT \
           --region=$GOOGLE_CLOUD_LOCATION \
           --agent=adk-sql-agent
```

## Cloud Run Deployment

Cloud Run is an alternative deployment option with broader regional availability.

### Advantages of Cloud Run
- Available in more regions
- Direct HTTP endpoint access
- Familiar container-based deployment
- Pay-per-use pricing

### Deployment Steps

1. **Set Environment Variables**
   ```bash
   export GOOGLE_CLOUD_PROJECT=your-project-id
   export GOOGLE_CLOUD_LOCATION=us-central1
   ```

2. **Deploy**
   ```bash
   ./deploy_cloudrun.sh
   ```

3. **Get Service URL**
   ```bash
   gcloud run services describe adk-sql-agent \
     --platform managed \
     --region $GOOGLE_CLOUD_LOCATION \
     --format='value(status.url)'
   ```

4. **Test the Deployment**
   ```bash
   # Health check
   curl https://YOUR-SERVICE-URL/status
   
   # Send a query
   curl -X POST https://YOUR-SERVICE-URL/query \
     -H 'Content-Type: application/json' \
     -d '{
       "query": "Show me the top 10 customers by revenue",
       "history": []
     }'
   ```

### Cloud Run Commands

```bash
# View service details
gcloud run services describe adk-sql-agent \
  --region=$GOOGLE_CLOUD_LOCATION

# Update service
gcloud run services update adk-sql-agent \
  --region=$GOOGLE_CLOUD_LOCATION \
  --memory 8Gi

# View logs
gcloud run services logs read adk-sql-agent \
  --region=$GOOGLE_CLOUD_LOCATION \
  --limit=50

# Delete service
gcloud run services delete adk-sql-agent \
  --region=$GOOGLE_CLOUD_LOCATION
```

## Configuration

### Environment Variables

Both deployment methods require these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_GENAI_USE_VERTEXAI` | Use Vertex AI for Gemini | `TRUE` |
| `GOOGLE_CLOUD_PROJECT` | Your GCP project ID | `my-project-123` |
| `GOOGLE_CLOUD_LOCATION` | Deployment region | `us-central1` |

### Resource Configuration

Adjust resources in `agent_engine.yaml` or deployment scripts:

```yaml
resources:
  cpu: "2"        # CPU cores
  memory: "4Gi"   # Memory allocation
```

For Cloud Run:
```bash
--memory 4Gi --cpu 2
```

### Scaling Configuration

**Agent Engine** (`agent_engine.yaml`):
```yaml
scaling:
  minInstances: 1
  maxInstances: 10
```

**Cloud Run**:
```bash
--min-instances 1 --max-instances 10
```

## Monitoring and Troubleshooting

### View Logs

**Agent Engine**:
```bash
gcloud logging read "resource.type=cloud_run_revision" \
  --project=$GOOGLE_CLOUD_PROJECT \
  --limit=50
```

**Cloud Run**:
```bash
gcloud run services logs read adk-sql-agent \
  --region=$GOOGLE_CLOUD_LOCATION \
  --limit=50
```

### Common Issues

#### 1. Permission Denied Errors
**Solution**: Ensure the service account has the required roles:
```bash
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
  --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
  --role="roles/aiplatform.user"
```

#### 2. Out of Memory Errors
**Solution**: Increase memory allocation:
```bash
# For Cloud Run
gcloud run services update adk-sql-agent \
  --memory 8Gi \
  --region=$GOOGLE_CLOUD_LOCATION
```

#### 3. Timeout Errors
**Solution**: Increase timeout:
```bash
# For Cloud Run
gcloud run services update adk-sql-agent \
  --timeout 600 \
  --region=$GOOGLE_CLOUD_LOCATION
```

#### 4. Cold Start Issues
**Solution**: Set minimum instances:
```bash
# For Cloud Run
gcloud run services update adk-sql-agent \
  --min-instances 1 \
  --region=$GOOGLE_CLOUD_LOCATION
```

### Monitoring Dashboard

Access Cloud Run metrics in the Google Cloud Console:
1. Navigate to Cloud Run
2. Select your service
3. Click on "Metrics" tab

Key metrics to monitor:
- Request count
- Request latency
- Instance count
- Memory utilization
- CPU utilization

### Cost Optimization

1. **Use minimum instances wisely**: Set to 0 for dev, 1+ for production
2. **Right-size resources**: Start with 2 CPU / 4Gi and adjust based on metrics
3. **Set max instances**: Prevent runaway costs with reasonable limits
4. **Use Cloud Run for variable traffic**: Pay only for actual usage

## Production Checklist

Before deploying to production:

- [ ] Set up proper authentication (remove `--allow-unauthenticated`)
- [ ] Configure custom domain
- [ ] Set up monitoring alerts
- [ ] Enable Cloud Armor for DDoS protection
- [ ] Configure VPC connector for private resources
- [ ] Set up CI/CD pipeline
- [ ] Configure backup and disaster recovery
- [ ] Review and optimize costs
- [ ] Set up proper logging and monitoring
- [ ] Configure secrets management for sensitive data

## Next Steps

1. **Integrate with Streamlit**: Deploy the Streamlit frontend separately
2. **Add Authentication**: Implement IAM or OAuth
3. **Set up CI/CD**: Automate deployments with Cloud Build
4. **Monitor Performance**: Set up alerts and dashboards
5. **Scale Testing**: Load test your deployment

## Support

For issues and questions:
- ADK Documentation: https://cloud.google.com/adk/docs
- Cloud Run Documentation: https://cloud.google.com/run/docs
- GitHub Issues: [Your repo issues page]
