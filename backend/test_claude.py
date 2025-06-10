"""
Quick test script to verify Claude API integration.
Run this to test your API key and basic functionality.
"""
import asyncio
import os
from dotenv import load_dotenv
import anthropic


async def test_basic_claude():
    """Test basic Claude API functionality."""
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not found in .env file")
        return False
    
    print("✓ API key found")
    
    try:
        # Test basic API call
        client = anthropic.Anthropic(api_key=api_key)
        
        print("Testing Claude API...")
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": "Say 'Hello from RevBot!' if you can hear me."
            }]
        )
        
        print(f"✓ Claude response: {response.content[0].text}")
        
        # Test with tools
        print("\nTesting Claude with tools...")
        tool_response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            tools=[{
                "name": "test_tool",
                "description": "A test tool",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"}
                    },
                    "required": ["message"]
                }
            }],
            messages=[{
                "role": "user",
                "content": "Use the test_tool to say hello"
            }]
        )
        
        for block in tool_response.content:
            if hasattr(block, 'name'):
                print(f"✓ Tool use detected: {block.name}")
        
        print("\n✅ All tests passed! Claude integration is working.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    asyncio.run(test_basic_claude())