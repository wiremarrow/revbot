"""
Tools available to Claude for Revit automation.
"""
from typing import List, Dict, Any
from .code_generator import CodeGeneratorTool
from .pyrevit_executor import PyRevitExecutorTool
from ..models.tools import Tool


# Registry of available tools
TOOL_REGISTRY = {
    "generate_revit_code": CodeGeneratorTool(),
    "execute_pyrevit_script": PyRevitExecutorTool(),
}


def get_available_tools() -> List[Tool]:
    """Get list of all available tools."""
    return [tool.definition for tool in TOOL_REGISTRY.values()]


async def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> Any:
    """Execute a tool by name with given parameters."""
    if tool_name not in TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {tool_name}")
    
    tool = TOOL_REGISTRY[tool_name]
    return await tool.execute(**parameters)