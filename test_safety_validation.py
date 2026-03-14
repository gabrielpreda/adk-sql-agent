"""
Test script to verify the safety validation logic works correctly.
This is a standalone test that doesn't require the full environment.
"""

def validate_sql_query(sql_query):
    """
    Validates SQL query for dangerous operations.
    Returns (is_safe, message)
    """
    if not sql_query:
        return False, "Empty query"
    
    sql_upper = sql_query.upper().strip()
    
    # List of dangerous SQL operations that should be blocked
    dangerous_operations = [
        'DROP TABLE',
        'DROP DATABASE',
        'TRUNCATE',
        'DELETE FROM',
        'ALTER TABLE',
        'CREATE TABLE',
        'CREATE DATABASE',
        'INSERT INTO',
        'UPDATE ',
        'GRANT ',
        'REVOKE ',
    ]
    
    for operation in dangerous_operations:
        if operation in sql_upper:
            return False, f"UNAUTHORIZED OPERATION: SQL query contains '{operation}' which is not allowed. Only SELECT queries are permitted."
    
    return True, "Query is safe"

def test_safety_validation():
    """Test that dangerous SQL operations are blocked."""
    
    print("Testing Safety Validation Logic")
    print("=" * 60)
    
    # Test cases for unauthorized operations
    unauthorized_queries = [
        ("DROP TABLE books", "DROP TABLE"),
        ("DELETE FROM customers", "DELETE FROM"),
        ("TRUNCATE TABLE orders", "TRUNCATE"),
        ("ALTER TABLE books ADD COLUMN test VARCHAR(100)", "ALTER TABLE"),
        ("DROP DATABASE bookstore", "DROP DATABASE"),
        ("UPDATE books SET price = 0", "UPDATE"),
        ("INSERT INTO books VALUES (1, 'Test', 'Test', 10)", "INSERT INTO"),
        # Note: Natural language like "delete entire database" is caught by the 
        # Safety Validator agent (LLM-based) before SQL generation
    ]
    
    # Test cases for authorized operations (should pass)
    authorized_queries = [
        "SELECT * FROM books LIMIT 10",
        "SELECT title, author FROM books WHERE price > 10",
        "SELECT COUNT(*) FROM customers",
        "SELECT b.title, a.name FROM books b JOIN authors a ON b.author_id = a.id",
    ]
    
    print("\n1. Testing UNAUTHORIZED operations (should be blocked):")
    print("-" * 60)
    
    passed = 0
    failed = 0
    
    for query, operation in unauthorized_queries:
        print(f"\nTesting: {query}")
        is_safe, message = validate_sql_query(query)
        
        if not is_safe:
            print(f"✓ BLOCKED: {operation} operation correctly rejected")
            print(f"  Message: {message}")
            passed += 1
        else:
            print(f"✗ FAILED: {operation} operation was NOT blocked!")
            failed += 1
    
    print("\n\n2. Testing AUTHORIZED operations (should succeed):")
    print("-" * 60)
    
    for query in authorized_queries:
        print(f"\nTesting: {query}")
        is_safe, message = validate_sql_query(query)
        
        if is_safe:
            print(f"✓ ALLOWED: Query is safe")
            passed += 1
        else:
            print(f"✗ FAILED: Valid SELECT query was incorrectly blocked!")
            print(f"  Message: {message}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Safety Validation Testing Complete")
    print(f"Passed: {passed}, Failed: {failed}")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = test_safety_validation()
    exit(0 if success else 1)
