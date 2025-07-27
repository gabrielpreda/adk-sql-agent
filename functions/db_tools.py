from google.adk.tools.base_tool import BaseTool
import ast
from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri("sqlite:///data/Chinook_Sqlite.sqlite")


class GetSchemaTool(BaseTool):
    name = "get_schema_tool"
    description = "Gets the database schema"

    def run(self, input: dict = None) -> dict:
        schema = db.get_table_info()
        print(schema)
        return {"schema_description": schema}


class RunSQLQueryTool(BaseTool):
    name = "run_sql_query_tool"
    description = "Runs a SQL query and returns the result"

    def run(self, input: dict) -> dict:
        sql_query = input.get("query")
        try:
            result = db.run(sql_query)
            result = ast.literal_eval(result)
            print(result)
            return {"raw_result": result}
        except Exception as ex:
            return {"error": str(ex)}
        
get_schema_tool = GetSchemaTool(
    name="get_schema_tool",
    description="Gets the database schema"
)

run_sql_query_tool = RunSQLQueryTool(
    name="run_sql_query_tool",
    description="Runs a SQL query and returns the result"
)