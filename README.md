# Introduction
The application uses ADK, Gemini, LangChain tools to power an SQL Agent.

# Architecture

Frontend: Streamlit app (streamlit_ui.py)   
Backend: FastAPI service (main.py)   
Agents:   
* **Coordinator**: sql_agent (sql_agent.py)  
* **Subagents**:  
    * **Rephraser** agent (rewrite_prompt.py)
    * **Generator** agent (generator.py)
    * **Analyzer** agent (analyzer.py)
    * **Reflexion** agent (reflexion.py)
    * **Routing** agent (routing.py)



Function Tools:  
* **get_schema** tool (db_tools.py)  
* **run_sql_query** tool (db_tools.py)  

Models:  
* Gemini 2.5 pro  

# Getting started

## Clone the repo

```bash
git clone https://github.com/gabrielpreda/adk-sql-agent.git
cd adk-sql-agent
```

## Create an .env file

The file should contain the following:
```
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT
GOOGLE_CLOUD_LOCATION=YOUR_REGION
```

## Install dependencies

Run:
```bash
pip install -r requirements.txt
```

## Start the backend

Run:
```bash
uvicorn main:app --reload
```

## Start the frontend

Run:
```bash
streamlit run streamlit_ui.py
```

## Testing

From the root folder run:
```bash
adk web
```
Then select the `sql_agent` folder. ADK web will discover in `agent.py` the `root_agent` and you will be able to test, monitor, debug the application.

The Agentic workflow is shown in the following figure (current step: Generator agent receives the result from `run_sql_query` tool).

<img src="assets/adk_web_1.png" width=900></img>

The next figure shows the result of Generator Agent.

<img src="assets/adk_web_2.png" width=900></img>

The next figure shows:
- Result of Analyzer Agent.
- Resolution of the Reflection Agent, based on previous agent analysis.
- The rationale for Routing Agent to route to Rewrite Query Agent.
- The reasoning of Rewrite Query Agent and the new query generated.

<img src="assets/adk_web_3.png" width=900></img>


## Deployment

### Option 1: Deploy to Agent Engine (Recommended)

Agent Engine is Google Cloud's managed service for deploying ADK agents.

#### Prerequisites
- Google Cloud Project with billing enabled
- gcloud CLI installed and configured
- ADK CLI version 1.3.0+

#### Deploy

1. Set your project ID and region:
```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
```

2. Run the deployment script:
```bash
./deploy.sh
```

3. Test your deployed agent:
```bash
adk run --project=$GOOGLE_CLOUD_PROJECT --region=$GOOGLE_CLOUD_LOCATION --agent=adk-sql-agent
```

### Option 2: Deploy to Cloud Run

Alternative deployment using Google Cloud Run for broader region availability.

#### Deploy

1. Set your project ID and region:
```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
```

2. Run the Cloud Run deployment script:
```bash
./deploy_cloudrun.sh
```

3. The script will output your service URL. Test it:
```bash
# Check status
curl https://your-service-url/status

# Send a query
curl -X POST https://your-service-url/query \
  -H 'Content-Type: application/json' \
  -d '{"query": "Show me the top 10 customers"}'
```

### Manual Deployment

If you prefer manual deployment:

```bash
# Build container
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/adk-sql-agent

# Deploy to Cloud Run
gcloud run deploy adk-sql-agent \
  --image gcr.io/$GOOGLE_CLOUD_PROJECT/adk-sql-agent \
  --platform managed \
  --region $GOOGLE_CLOUD_LOCATION \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_GENAI_USE_VERTEXAI=TRUE \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT \
  --set-env-vars GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION \
  --memory 4Gi \
  --cpu 2
```

## Demo

We show here the sequence of operations for one query.

### Rewrite prompt

<img src="assets/result_1.png" width=600></img>

### Generator results

<img src="assets/result_2.png" width=600></img>

### Analyzer + Reflection

<img src="assets/result_3.png" width=600></img>


### Reflection resolution

<img src="assets/result_6.png" width=600></img>

### Results

<img src="assets/result_4.png" width=600></img>