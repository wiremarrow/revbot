"""
Service for code generation and execution.
"""
from typing import Dict, Any, List, Optional
import time
import structlog

from ..core.claude_client import ClaudeClient
from ..tools import execute_tool, get_available_tools
from ..models.responses import ExecutionStatus

logger = structlog.get_logger(__name__)


class CodeService:
    """Service handling code generation and execution logic."""
    
    def __init__(self):
        self.claude_client = ClaudeClient()
    
    async def generate_code(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        Generate Revit API code using Claude with tools.
        
        Args:
            prompt: User's request
            context: Additional context about Revit environment
            conversation_history: Previous conversation messages
            temperature: Model temperature
            
        Returns:
            Dictionary with generated code and metadata
        """
        try:
            # Enhance prompt with context if provided
            enhanced_prompt = self._enhance_prompt(prompt, context)
            
            # Generate with Claude
            result = await self.claude_client.generate_with_tools(
                prompt=enhanced_prompt,
                conversation_history=conversation_history,
                temperature=temperature
            )
            
            # Extract code from response
            generated_code = self._extract_code_from_response(result["content"])
            
            return {
                "code": generated_code,
                "explanation": self._extract_explanation(result["content"]),
                "tool_results": result.get("tool_results", []),
                "confidence": 0.95,  # Could be calculated based on tool results
                "warnings": self._check_warnings(generated_code, context),
                "raw_response": result.get("content")
            }
            
        except Exception as e:
            logger.error("Code generation failed", error=str(e))
            raise
    
    async def execute_code(
        self,
        code: str,
        safe_mode: bool = True,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Execute code in Revit via pyRevit.
        
        Args:
            code: Python code to execute
            safe_mode: Whether to validate code before execution
            timeout: Execution timeout in seconds
            
        Returns:
            Dictionary with execution results
        """
        start_time = time.time()
        
        try:
            # Use the pyRevit executor tool
            result = await execute_tool(
                "execute_pyrevit_script",
                {
                    "code": code,
                    "timeout": timeout,
                    "capture_output": True
                }
            )
            
            execution_time = time.time() - start_time
            
            if result.get("success"):
                return {
                    "status": ExecutionStatus.SUCCESS,
                    "output": result.get("output", ""),
                    "execution_time": execution_time,
                    "revit_state": result.get("revit_state", {})
                }
            else:
                return {
                    "status": ExecutionStatus.ERROR,
                    "error": result.get("error", "Unknown error"),
                    "output": result.get("output", ""),
                    "execution_time": execution_time
                }
                
        except Exception as e:
            logger.error("Code execution failed", error=str(e))
            return {
                "status": ExecutionStatus.ERROR,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    def get_available_tools(self):
        """Get list of available tools."""
        return get_available_tools()
    
    def _enhance_prompt(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        """Enhance prompt with context information."""
        if not context:
            return prompt
        
        context_parts = []
        
        if "active_view" in context:
            context_parts.append(f"Active view: {context['active_view']}")
        
        if "selected_elements" in context:
            count = len(context["selected_elements"])
            context_parts.append(f"Selected elements: {count}")
        
        if "document_info" in context:
            doc_info = context["document_info"]
            if "is_workshared" in doc_info:
                context_parts.append(f"Workshared: {doc_info['is_workshared']}")
        
        if context_parts:
            context_str = "\n".join(context_parts)
            return f"{prompt}\n\nContext:\n{context_str}"
        
        return prompt
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract Python code from Claude's response."""
        # Look for code blocks
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()
        
        # If no code blocks, assume the entire response is code
        # (This might happen with direct tool responses)
        return response.strip()
    
    def _extract_explanation(self, response: str) -> Optional[str]:
        """Extract explanation from response."""
        # Look for explanation outside code blocks
        if "```" in response:
            # Get text before first code block
            first_code = response.find("```")
            if first_code > 0:
                explanation = response[:first_code].strip()
                if explanation:
                    return explanation
            
            # Get text after last code block
            last_code_end = response.rfind("```")
            if last_code_end > 0:
                last_code_end = response.find("\n", last_code_end)
                if last_code_end > 0 and last_code_end < len(response) - 1:
                    explanation = response[last_code_end:].strip()
                    if explanation:
                        return explanation
        
        return None
    
    def _check_warnings(self, code: str, context: Optional[Dict[str, Any]]) -> Optional[List[str]]:
        """Check for potential warnings in generated code."""
        warnings = []
        
        code_lower = code.lower()
        
        # Check for potentially dangerous operations
        if "delete" in code_lower or "doc.delete" in code_lower:
            warnings.append("Code contains delete operations - ensure you have backups")
        
        if "transaction" not in code_lower:
            warnings.append("Code may not be wrapped in a transaction - changes might not persist")
        
        if context and context.get("is_workshared"):
            if "worksharing" not in code_lower:
                warnings.append("This is a workshared model - ensure proper element ownership")
        
        return warnings if warnings else None