"""
Example usage of the RevBot API.
"""
import asyncio
import httpx
import json
from typing import Dict, Any


API_BASE_URL = "http://localhost:8000/api/v1"


async def test_code_generation():
    """Test code generation endpoint."""
    # Increase timeout for Claude API calls
    timeout = httpx.Timeout(120.0)  # 2 minutes
    async with httpx.AsyncClient(timeout=timeout) as client:
        # Example 1: Simple wall creation
        response = await client.post(
            f"{API_BASE_URL}/generate",
            json={
                "prompt": "Create a wall from point (0,0,0) to point (10,0,0) on Level 1",
                "temperature": 0.2
            }
        )
        
        print("Code Generation Response:")
        print(json.dumps(response.json(), indent=2))
        print("\n" + "="*50 + "\n")
        
        return response.json()


async def test_code_execution(code: str):
    """Test code execution endpoint."""
    timeout = httpx.Timeout(120.0)  # 2 minutes
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{API_BASE_URL}/execute",
            json={
                "code": code,
                "safe_mode": True,
                "timeout": 30
            }
        )
        
        print("Code Execution Response:")
        print(json.dumps(response.json(), indent=2))
        print("\n" + "="*50 + "\n")
        
        return response.json()


async def test_chat_endpoint():
    """Test combined chat endpoint."""
    timeout = httpx.Timeout(120.0)  # 2 minutes
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{API_BASE_URL}/chat",
            params={
                "prompt": "Create a simple room with four walls",
                "execute_code": False  # Set to True to auto-execute
            }
        )
        
        print("Chat Response:")
        print(json.dumps(response.json(), indent=2))
        print("\n" + "="*50 + "\n")
        
        return response.json()


async def test_list_tools():
    """Test listing available tools."""
    timeout = httpx.Timeout(60.0)  # 1 minute (tools endpoint is faster)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(f"{API_BASE_URL}/tools")
        
        print("Available Tools:")
        print(json.dumps(response.json(), indent=2))
        print("\n" + "="*50 + "\n")
        
        return response.json()


async def main():
    """Run all tests."""
    print("Testing RevBot API...\n")
    print("⏳ Note: API calls may take 30-60 seconds due to Claude processing time\n")
    
    try:
        # Test 1: List available tools
        print("1. Listing available tools...")
        await test_list_tools()
        
        # Test 2: Generate code
        print("2. Testing code generation...")
        print("   ⏳ Calling Claude API (this may take up to 2 minutes)...")
        generation_result = await test_code_generation()
        
        # Test 3: Execute code (if generation was successful)
        if generation_result.get("code"):
            print("3. Testing code execution...")
            await test_code_execution(generation_result["code"])
        
        # Test 4: Chat endpoint
        print("4. Testing chat endpoint...")
        print("   ⏳ Calling Claude API...")
        await test_chat_endpoint()
        
        print("✅ All tests completed!")
        
    except httpx.ReadTimeout:
        print("❌ Error: Request timed out.")
        print("   This usually means Claude API is taking longer than expected.")
        print("   Try running the test again or check your internet connection.")
    except httpx.ConnectTimeout:
        print("❌ Error: Could not connect to the server.")
        print("   Make sure the RevBot server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("   Check that the server is running and your API key is configured.")


if __name__ == "__main__":
    asyncio.run(main())