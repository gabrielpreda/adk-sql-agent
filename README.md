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



