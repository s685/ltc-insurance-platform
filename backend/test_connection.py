"""Test Snowflake connection with current credentials."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import get_settings
from snowflake.snowpark import Session

def test_connection():
    """Test Snowflake connection."""
    print("\n" + "="*60)
    print("Testing Snowflake Connection")
    print("="*60 + "\n")
    
    settings = get_settings()
    
    print("Configuration loaded:")
    print(f"  Account: {settings.snowflake_account}")
    print(f"  User: {settings.snowflake_user}")
    print(f"  Warehouse: {settings.snowflake_warehouse}")
    print(f"  Database: {settings.snowflake_database}")
    print(f"  Schema: {settings.snowflake_schema}")
    print()
    
    # Check for placeholder values
    if any([
        settings.snowflake_account == "your_account",
        settings.snowflake_user == "your_user",
        settings.snowflake_warehouse == "your_warehouse",
        "your_" in settings.snowflake_password.lower()
    ]):
        print("[ERROR] You are still using placeholder values!")
        print("\nPlease update your .env file with REAL Snowflake credentials:")
        print("  1. Open: backend\\.env")
        print("  2. Replace 'your_account', 'your_user', etc. with actual values")
        print("  3. Save the file")
        print("  4. Run this test again")
        print("\nExample of what to change:")
        print("  BEFORE: SNOWFLAKE_ACCOUNT=your_account")
        print("  AFTER:  SNOWFLAKE_ACCOUNT=abc12345.us-east-1")
        return False
    
    print("Attempting to connect to Snowflake...")
    
    try:
        connection_params = settings.snowflake_connection_params
        session = Session.builder.configs(connection_params).create()
        
        # Test query
        result = session.sql("SELECT CURRENT_TIMESTAMP() as ts, CURRENT_USER() as user").collect()
        
        print("\n[SUCCESS] Connected to Snowflake!")
        print(f"  Timestamp: {result[0]['TS']}")
        print(f"  User: {result[0]['USER']}")
        print(f"  Session ID: {session.session_id}")
        
        # Check if database and schema exist
        try:
            session.sql(f"USE DATABASE {settings.snowflake_database}").collect()
            session.sql(f"USE SCHEMA {settings.snowflake_schema}").collect()
            print(f"\n[SUCCESS] Database and Schema accessible!")
        except Exception as e:
            print(f"\n[WARNING] Cannot access {settings.snowflake_database}.{settings.snowflake_schema}")
            print(f"   Error: {str(e)}")
            print(f"   You may need to create the database/schema or check permissions")
        
        session.close()
        print("\n" + "="*60)
        print("Connection test completed successfully!")
        print("="*60 + "\n")
        return True
        
    except Exception as e:
        print(f"\n[CONNECTION FAILED]")
        print(f"Error: {str(e)}\n")
        
        error_str = str(e).lower()
        if "404" in error_str or "not found" in error_str:
            print("Troubleshooting tips:")
            print("  - Check your SNOWFLAKE_ACCOUNT value")
            print("  - Make sure it's in format: accountname.region")
            print("  - Example: abc12345.us-east-1")
            print("  - Don't include '.snowflakecomputing.com'")
        elif "authentication" in error_str or "password" in error_str:
            print("Troubleshooting tips:")
            print("  - Check your username and password")
            print("  - Make sure there are no extra spaces")
            print("  - Verify credentials work in Snowflake web UI")
        elif "warehouse" in error_str:
            print("Troubleshooting tips:")
            print("  - Check your SNOWFLAKE_WAREHOUSE value")
            print("  - Make sure the warehouse exists and you have access")
        
        print("\n" + "="*60)
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

