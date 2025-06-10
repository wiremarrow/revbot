"""
Tool definitions for Claude agent.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
from enum import Enum


class ParameterType(str, Enum):
    """Supported parameter types for tools."""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


class ToolParameter(BaseModel):
    """Definition of a tool parameter."""
    name: str
    type: ParameterType
    description: str
    required: bool = True
    default: Optional[Any] = None
    
    class Config:
        use_enum_values = True


class Tool(BaseModel):
    """Definition of a tool available to Claude."""
    name: str
    description: str
    parameters: List[ToolParameter]
    
    def to_anthropic_format(self) -> Dict[str, Any]:
        """Convert to Anthropic's tool format."""
        properties = {}
        required = []
        
        for param in self.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description
            }
            if param.default is not None:
                properties[param.name]["default"] = param.default
            if param.required:
                required.append(param.name)
        
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }


class ToolResponse(BaseModel):
    """Response from tool execution."""
    tool_use_id: str
    output: Union[str, Dict[str, Any]]
    is_error: bool = False