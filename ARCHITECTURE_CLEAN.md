# Authorization System - Final Clean Architecture

## Overview

Simple, clean three-step pipeline:
1. **Safety Check** - Determines if request is secure
2. **Security Router** - Routes based on security (exit OR continue)
3. **Refinement Loop** - Processes query (only if secure)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      User Request                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────────┐
         │   STEP 1: Safety Check Agent      │
         │   Determines: SECURE / NOT SECURE │
         │   Output: {is_secure: bool}       │
         └────────────────┬──────────────────┘
                          │
                          ▼
         ┌───────────────────────────────────┐
         │   STEP 2: Security Router Agent   │
         │   Routes based on is_secure       │
         └────────┬──────────────────┬───────┘
                  │                  │
         NOT SECURE                SECURE
                  │                  │
                  ▼                  ▼
    ┌─────────────────────┐   ┌──────────────────────┐
    │ Output: Rejection   │   │ Output: "Proceeding" │
    │ Message             │   │                      │
    │ EXIT IMMEDIATELY ✓  │   │ CONTINUE ✓           │
    └─────────────────────┘   └──────────┬───────────┘
                                          │
                                          ▼
                          ┌───────────────────────────────┐
                          │ STEP 3: Refinement Loop       │
                          │ - Rewrite Prompt (passthrough)│
                          │ - Generator                   │
                          │ - Analyzer                    │
                          │ - Reflexion                   │
                          │ - Routing                     │
                          └───────────────┬───────────────┘
                                          │
                                          ▼
                                    Query Results
```

## How It Works

### Step 1: Safety Check Agent
**Purpose**: Determine if the request is secure

**Input**: User's natural language request

**Processing**:
- Analyzes the request intent
- Checks against unauthorized operations list
- Makes a binary decision

**Output**:
```json
{
  "is_secure": true/false,
  "reason": "Brief explanation"
}
```

**Examples**:
- "delete entire database" → `{is_secure: false, reason: "Attempts to delete database"}`
- "show top 10 books" → `{is_secure: true, reason: "Read-only SELECT query"}`

### Step 2: Security Router Agent
**Purpose**: Route based on security decision

**Input**: 
- `is_secure`: boolean from safety check
- `reason`: explanation
- `user_input`: original request

**Processing**:
- If `is_secure = false`: Generate final rejection message
- If `is_secure = true`: Generate "proceeding" message

**Output**:
- **NOT SECURE**: "I cannot perform this operation. Your request attempts to [operation], which is not authorized. This system only allows read-only SELECT queries."
- **SECURE**: "Security check passed. Proceeding with your request..."

**Critical Behavior**:
- NOT SECURE output is the **FINAL user message**
- SECURE output is a status message, processing continues

### Step 3: Refinement Loop
**Purpose**: Generate and execute SQL query

**Input**: Output from security router

**Processing**:
- **Rewrite Prompt Agent**: 
  - Detects security messages (rejection or "proceeding")
  - Passes through unchanged if security message
  - Rewrites if normal request
- **Generator Agent**: Generates SQL
- **Analyzer Agent**: Analyzes results
- **Reflexion Agent**: Decides GO/NO-GO
- **Routing Agent**: Routes based on decision

**Output**: Query results or error message

## Example Flows

### Example 1: Unauthorized Request

```
User: "delete entire database"
    ↓
┌─────────────────────────────────────────┐
│ Step 1: Safety Check Agent              │
│ Analysis: "Attempts to delete database" │
│ Output: {is_secure: false}              │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Security Router Agent                               │
│ Decision: NOT SECURE                                        │
│ Output: "I cannot perform this operation. Your request      │
│          attempts to delete the entire database, which is   │
│          not authorized for security reasons. This system   │
│          only allows read-only SELECT queries."             │
└─────────────────┬───────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ Step 3: Refinement Loop                 │
│ Rewrite Prompt: Detects rejection msg   │
│ Action: Pass through unchanged          │
│ Output: Same rejection message          │
└─────────────────┬───────────────────────┘
                  ↓
        User receives rejection
        ✓ NO SQL GENERATED
        ✓ IMMEDIATE EXIT
```

### Example 2: Authorized Request

```
User: "show me the top 10 most expensive books"
    ↓
┌─────────────────────────────────────────┐
│ Step 1: Safety Check Agent              │
│ Analysis: "Read-only SELECT query"      │
│ Output: {is_secure: true}               │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ Step 2: Security Router Agent           │
│ Decision: SECURE                        │
│ Output: "Security check passed.         │
│          Proceeding with your request..." │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ Step 3: Refinement Loop                 │
│ Rewrite Prompt: Detects "Security check"│
│ Action: Pass through                    │
│ Generator: Generates SQL                │
│   SELECT * FROM books                   │
│   ORDER BY price DESC LIMIT 10          │
│ Analyzer: Analyzes results              │
│ Reflexion: GO (success)                 │
│ Routing: Return results                 │
└─────────────────┬───────────────────────┘
                  ↓
        User receives query results
        ✓ SQL GENERATED AND EXECUTED
        ✓ RESULTS RETURNED
```

## Key Components

### 1. Safety Check Agent (`sql_agent/agent.py`)
```python
- Input: user_input
- Output: {is_secure: bool, reason: str}
- Model: gemini-2.5-pro
- Purpose: Binary security decision
```

### 2. Security Router Agent (`sql_agent/agent.py`)
```python
- Input: {is_secure: bool, reason: str, user_input: str}
- Output: rejection message OR "proceeding" message
- Model: gemini-2.5-pro
- Purpose: Route based on security
```

### 3. Rewrite Prompt Agent (`subagents/rewrite_prompt.py`)
```python
- Input: {user_input: str, db_schema: str, feedback: Optional[str]}
- Output: rewritten prompt OR passthrough message
- Model: gemini-2.5-pro
- Purpose: Rewrite for SQL generation, passthrough security messages
```

### 4. SQL-Level Validation (`functions/db_tools.py`)
```python
- Input: SQL query string
- Output: results OR error
- Purpose: Second layer of defense at execution level
```

## Benefits

1. ✅ **Clean Architecture**: Simple three-step pipeline
2. ✅ **Clear Separation**: Security check → Router → Processing
3. ✅ **Immediate Exit**: Router outputs final message on NOT SECURE
4. ✅ **Smart Passthrough**: Rewrite agent detects and passes security messages
5. ✅ **Multi-Layer Defense**: Safety check + SQL-level validation
6. ✅ **Easy to Understand**: Each agent has one clear responsibility

## Technical Notes

### ADK SequentialAgent Behavior
- ADK's `SequentialAgent` executes all sub-agents in sequence
- Cannot skip agents based on conditions
- Our solution: Use passthrough mechanism
  - Router outputs terminal message on NOT SECURE
  - Rewrite agent detects and passes through
  - Effectively prevents SQL generation

### Passthrough Detection
Rewrite Prompt Agent detects:
- Messages starting with "I cannot perform this operation"
- Messages containing "Security check passed"
- Any security-related messages

When detected:
- Outputs message unchanged
- No rewriting occurs
- No SQL generation occurs

## Files

- **`sql_agent/agent.py`**: Main pipeline with all three agents
- **`subagents/rewrite_prompt.py`**: Passthrough logic
- **`functions/db_tools.py`**: SQL-level validation

## Testing

Test unauthorized request:
```python
# Input: "delete entire database"
# Expected: Rejection message, no SQL generation
```

Test authorized request:
```python
# Input: "show me top 10 books"
# Expected: SQL generation and execution
```

## Summary

This is the **simplest, cleanest architecture** for authorization:

1. **Check** security (binary decision)
2. **Route** based on decision (exit OR continue)
3. **Process** if secure (SQL generation and execution)

The passthrough mechanism ensures that rejection messages reach the user immediately without any SQL processing, effectively implementing the "exit immediately on not secure" requirement.
