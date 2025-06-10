"""
Test RevBot with the simplest possible pyRevit script.
Run this after starting RevBot to test basic execution.
"""
import asyncio
import httpx
import json


async def test_simple_execution():
    """Test executing the simplest possible pyRevit script."""
    
    # The simplest possible pyRevit code
    simple_code = '''# Simple test
print("Hello from RevBot!")
print("Timestamp: " + str(__import__('datetime').datetime.now()))
print("pyRevit execution successful!")'''
    
    print("Testing RevBot pyRevit execution...")
    print("=" * 50)
    print("Code to execute:")
    print(simple_code)
    print("=" * 50)
    
    # Test execution
    timeout = httpx.Timeout(30.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/v1/execute",
                json={
                    "code": simple_code,
                    "safe_mode": True,
                    "timeout": 30
                }
            )
            
            result = response.json()
            
            print("\nResponse Status:", result.get("status"))
            print("\nOutput:", result.get("output", "No output"))
            print("\nError:", result.get("error", "No error"))
            
            if result.get("debug_info"):
                print("\nDebug Info:")
                print(json.dumps(result["debug_info"], indent=2))
            
            print("\n" + "=" * 50)
            
            if result.get("status") == "success":
                print("✅ SUCCESS: pyRevit execution is working!")
            else:
                print("❌ FAILED: See error details above")
                print("\nTroubleshooting:")
                print("1. Run test_pyrevit.bat first to verify pyRevit CLI")
                print("2. Ensure Revit is running with a document open")
                print("3. Check that pyRevit tab is visible in Revit")
            
        except Exception as e:
            print(f"❌ Error calling RevBot API: {e}")


if __name__ == "__main__":
    print("RevBot Simple Execution Test")
    print("Make sure RevBot is running on http://localhost:8000")
    print()
    asyncio.run(test_simple_execution())