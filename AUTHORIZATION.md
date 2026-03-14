# Authorization and Safety System

## Overview

The SQL Agent now includes a comprehensive multi-layered authorization and safety system to prevent unauthorized and dangerous operations. The system ensures that only safe, read-only SQL queries are executed.

## Architecture

The authorization system operates at **three levels**:

### 1. User Input Validation (Safety Validator Agent)
**Location**: `subagents/safety_validator.py`

This is the **first line of defense** that runs before any SQL generation or execution.

- **When**: Immediately when a user request is received
- **What**: Uses LLM (Gemini 2.5 Pro) to analyze the user's natural language request
- **How**: Identifies dangerous intent like "delete entire database", "drop all tables", etc.
- **Output**: 
  - `GO` - Request is safe and authorized
  - `NO-GO` - Request is unsafe/unauthorized
- **Action on NO-GO**: System exits immediately via Safety Routing Agent

**Blocked Operations**:
- Deleting entire databases or tables
- Deleting all records from tables
- Truncating tables
- Altering database schema
- Any administrative or destructive operations

**Allowed Operations**:
- SELECT queries (read-only)
- Queries with specific WHERE clauses
- Aggregations, joins, analytical queries
- Data exploration and reporting

### 2. Safety Routing Agent
**Location**: `subagents/safety_routing.py`

This agent handles the immediate exit when unauthorized operations are detected.

- **When**: Immediately after Safety Validator Agent
- **What**: Routes based on the safety validation decision
- **Action on NO-GO**: 
  - Outputs a clear message to the user explaining why the operation is not permitted
  - **Forces immediate exit** from the entire pipeline
  - Prevents any further processing

### 3. SQL-Level Validation (Database Tools)
**Location**: `functions/db_tools.py`

This is the **second line of defense** that validates actual SQL queries before execution.

- **When**: Just before SQL query execution
- **What**: Pattern-matches SQL commands against a blocklist
- **How**: Checks for dangerous SQL keywords in the generated query

**Blocked SQL Operations**:
```python
- DROP TABLE
- DROP DATABASE
- TRUNCATE
- DELETE FROM
- ALTER TABLE
- CREATE TABLE
- CREATE DATABASE
- INSERT INTO
- UPDATE
- GRANT
- REVOKE
```

**Allowed SQL Operations**:
- SELECT statements (all variations)
- Read-only operations

## Flow Diagram

```
User Request
    ↓
[Safety Validator Agent] ← LLM analyzes user intent
    ↓
    ├─ GO → Continue to SQL generation
    │
    └─ NO-GO → [Safety Routing Agent] → EXIT IMMEDIATELY
                     ↓
                User receives rejection message


If GO:
    ↓
[Rewrite Prompt Agent]
    ↓
[Generator Agent] ← Generates SQL
    ↓
[SQL-Level Validation] ← Pattern matching on SQL
    ↓
    ├─ Safe → Execute query
    │
    └─ Unsafe → Return error → [Analyzer] → [Reflexion] → NO-GO → EXIT
```

## Integration with Existing Agents

### Reflexion Agent
**Updated**: `subagents/reflexion.py`

Now checks for "UNAUTHORIZED OPERATION" in analysis results and immediately outputs NO-GO.

### Routing Agent
**Updated**: `subagents/routing.py`

Enhanced to recognize unauthorized operations in feedback and force immediate exit without allowing retry or refinement.

### Main Agent Pipeline
**Updated**: `sql_agent/agent.py`

The pipeline now includes:
1. **Safety Check** (Safety Validator + Safety Routing) - runs first
2. **Refinement Loop** (existing agents) - only runs if safety check passes

## Testing

Run the test suite to verify the authorization system:

```bash
python test_safety_validation.py
```

This tests:
- ✓ All dangerous SQL operations are blocked
- ✓ All safe SELECT queries are allowed
- ✓ Proper error messages are returned

## Example Scenarios

### Scenario 1: Unauthorized Request (Natural Language)
**User Input**: "delete entire database"

**Flow**:
1. Safety Validator Agent analyzes request
2. Detects dangerous intent: database deletion
3. Returns: `decision="NO-GO"`, `reason="This request attempts to delete the entire database, which is not authorized."`
4. Safety Routing Agent receives NO-GO
5. **System exits immediately**
6. User receives: "I cannot perform this operation. This request attempts to delete the entire database, which is not authorized. Only read-only SELECT queries are permitted."

### Scenario 2: Unauthorized SQL Query
**User Input**: "Show me all customers" (safe request)
**Generated SQL**: `DELETE FROM customers` (somehow generated incorrectly)

**Flow**:
1. Safety Validator Agent: GO (user intent is safe)
2. SQL generation happens
3. SQL-Level Validation detects `DELETE FROM`
4. Returns: `{"error": "UNAUTHORIZED OPERATION: SQL query contains 'DELETE FROM' which is not allowed.", "unauthorized": True}`
5. Analyzer Agent analyzes the error
6. Reflexion Agent detects "UNAUTHORIZED OPERATION" in analysis
7. Returns: `decision="NO-GO"`, `feedback="Unauthorized operation detected"`
8. Routing Agent receives NO-GO with unauthorized operation
9. **System exits immediately**
10. User receives explanation

### Scenario 3: Authorized Request
**User Input**: "Show me the top 10 books by price"

**Flow**:
1. Safety Validator Agent: GO (read-only request)
2. Safety Routing Agent: Continue
3. SQL generation: `SELECT * FROM books ORDER BY price DESC LIMIT 10`
4. SQL-Level Validation: PASS (SELECT query)
5. Query executes successfully
6. Results returned to user

## Configuration

### Customizing Blocked Operations

To modify what operations are blocked, edit:

**For natural language validation**:
Edit the instruction prompt in `subagents/safety_validator.py`:
```python
instruction_prompt = """
...
**UNAUTHORIZED OPERATIONS** (must be rejected):
- Add your custom rules here
...
"""
```

**For SQL-level validation**:
Edit the `dangerous_operations` list in `functions/db_tools.py`:
```python
dangerous_operations = [
    'DROP TABLE',
    'DELETE FROM',
    # Add more patterns here
]
```

## Security Best Practices

1. **Defense in Depth**: Multiple validation layers ensure comprehensive protection
2. **Fail Secure**: System defaults to blocking when in doubt
3. **Immediate Exit**: No retry or refinement allowed for unauthorized operations
4. **Clear Communication**: Users receive clear explanations for rejections
5. **Logging**: All validation decisions are logged for audit purposes

## Limitations

1. **Pattern Matching**: SQL-level validation uses simple pattern matching, not full SQL parsing
2. **LLM Dependency**: User input validation relies on LLM understanding, which may have edge cases
3. **Read-Only Focus**: System is designed for read-only operations; write operations require separate authorization

## Future Enhancements

Potential improvements:
- Role-based access control (RBAC)
- Query complexity limits
- Rate limiting
- Audit logging to database
- Configurable authorization policies
- SQL parsing instead of pattern matching
