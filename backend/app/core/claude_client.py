"""
Claude API client with tool use support.
"""
import anthropic
from typing import List, Dict, Any, Optional, Union
import json
import structlog
from anthropic.types import Message, TextBlock, ToolUseBlock

from ..models.tools import Tool, ToolResponse
from ..tools import get_available_tools, execute_tool
from config.config import settings


logger = structlog.get_logger(__name__)


class ClaudeClient:
    """Client for interacting with Claude API with tool support."""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model
        self.max_tokens = settings.claude_max_tokens
        self.tools = get_available_tools()
        
    def _prepare_tools(self) -> List[Dict[str, Any]]:
        """Prepare tools in Anthropic format."""
        return [tool.to_anthropic_format() for tool in self.tools]
    
    async def generate_with_tools(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        Generate a response using Claude with tool support.
        
        Args:
            prompt: User's input prompt
            system_prompt: System instructions
            conversation_history: Previous messages
            temperature: Generation temperature
            
        Returns:
            Dictionary containing generated content and tool results
        """
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()
        
        messages = self._build_messages(prompt, conversation_history)
        tools = self._prepare_tools()
        
        try:
            # Initial request with tools
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=messages,
                tools=tools
            )
            
            # Process response and handle tool use
            final_response = await self._process_response(
                response, messages, system_prompt, temperature
            )
            
            return final_response
            
        except Exception as e:
            logger.error("Error generating with Claude", error=str(e))
            raise
    
    async def _process_response(
        self,
        response: Message,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float
    ) -> Dict[str, Any]:
        """Process Claude's response and handle tool calls."""
        result = {
            "content": "",
            "tool_results": [],
            "raw_response": response
        }
        
        # Extract content and tool uses
        for block in response.content:
            if isinstance(block, TextBlock):
                result["content"] += block.text
            elif isinstance(block, ToolUseBlock):
                # Execute the tool
                tool_result = await self._execute_tool_use(block)
                result["tool_results"].append(tool_result)
        
        # If tools were used, we need to continue the conversation
        if result["tool_results"]:
            # Add assistant's response with tool use
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Add tool results
            tool_results_content = []
            for tool_result in result["tool_results"]:
                tool_results_content.append({
                    "type": "tool_result",
                    "tool_use_id": tool_result["tool_use_id"],
                    "content": json.dumps(tool_result["output"])
                })
            
            messages.append({
                "role": "user",
                "content": tool_results_content
            })
            
            # Get final response after tool execution
            final_response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=messages
            )
            
            # Extract final content
            final_content = ""
            for block in final_response.content:
                if isinstance(block, TextBlock):
                    final_content += block.text
            
            result["content"] = final_content
            result["final_response"] = final_response
        
        return result
    
    async def _execute_tool_use(self, tool_use: ToolUseBlock) -> Dict[str, Any]:
        """Execute a tool use request from Claude."""
        logger.info(
            "Executing tool",
            tool_name=tool_use.name,
            tool_id=tool_use.id
        )
        
        try:
            output = await execute_tool(tool_use.name, tool_use.input)
            return {
                "tool_use_id": tool_use.id,
                "tool_name": tool_use.name,
                "success": True,
                "output": output
            }
        except Exception as e:
            logger.error(
                "Tool execution failed",
                tool_name=tool_use.name,
                error=str(e)
            )
            return {
                "tool_use_id": tool_use.id,
                "tool_name": tool_use.name,
                "success": False,
                "output": {"error": str(e)}
            }
    
    def _build_messages(
        self,
        prompt: str,
        conversation_history: Optional[List[Dict[str, str]]]
    ) -> List[Dict[str, str]]:
        """Build message list for Claude."""
        messages = []
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": prompt})
        
        return messages
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for Revit code generation."""
        return """You are an expert Revit API developer assistant. Your role is to help users write Python code for Revit automation using the Revit API and pyRevit.

Key guidelines:
1. Generate clean, well-structured Python code that follows Revit API best practices
2. Use appropriate error handling and transactions
3. Include necessary imports from Autodesk.Revit modules
4. Consider the user's context (active view, selection, etc.) when relevant
5. Explain complex operations clearly
6. Use the provided tools to validate and test code when appropriate

When generating code:
- Always wrap document modifications in a Transaction
- Use proper element filtering and selection methods
- Handle units correctly (Revit internal units vs display units)
- Follow pyRevit conventions when applicable

You have access to tools that can help you:
- generate_revit_code: Create Revit API code based on natural language descriptions
- execute_pyrevit_script: Test code in a Revit environment (use carefully)"""