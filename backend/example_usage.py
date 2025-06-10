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
    async with httpx.AsyncClient() as client:
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
    async with httpx.AsyncClient() as client:
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
    async with httpx.AsyncClient() as client:
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
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/tools")
        
        print("Available Tools:")
        print(json.dumps(response.json(), indent=2))
        print("\n" + "="*50 + "\n")
        
        return response.json()


async def main():
    """Run all tests."""
    print("Testing RevBot API...\n")
    
    # Test 1: List available tools
    print("1. Listing available tools...")
    await test_list_tools()
    
    # Test 2: Generate code
    print("2. Testing code generation...")
    generation_result = await test_code_generation()
    
    # Test 3: Execute code (if generation was successful)
    if generation_result.get("code"):
        print("3. Testing code execution...")
        await test_code_execution(generation_result["code"])
    
    # Test 4: Chat endpoint
    print("4. Testing chat endpoint...")
    await test_chat_endpoint()
    
    print("All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())