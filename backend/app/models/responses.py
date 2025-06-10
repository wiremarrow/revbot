"""
Response models for API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class ExecutionStatus(str, Enum):
    """Status of code execution."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    VALIDATION_FAILED = "validation_failed"


class ToolResult(BaseModel):
    """Result from a tool execution."""
    tool_name: str
    success: bool
    output: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CodeGenerationResponse(BaseModel):
    """Response model for code generation."""
    
    code: str = Field(..., description="Generated Python code for Revit")
    explanation: Optional[str] = Field(
        default=None,
        description="Explanation of the generated code"
    )
    tool_results: Optional[List[ToolResult]] = Field(
        default=None,
        description="Results from any tools used during generation"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Model's confidence in the generated code"
    )
    warnings: Optional[List[str]] = Field(
        default=None,
        description="Any warnings about the generated code"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Generation timestamp"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "# Create a wall\\nwall = Wall.Create(...)",
                "explanation": "This code creates a wall between two points",
                "confidence": 0.95,
                "timestamp": "2024-01-09T12:00:00Z"
            }
        }


class ExecutionResponse(BaseModel):
    """Response model for code execution."""
    
    status: ExecutionStatus = Field(..., description="Execution status")
    output: Optional[str] = Field(
        default=None,
        description="Output from the executed code"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if execution failed"
    )
    execution_time: float = Field(
        ...,
        description="Execution time in seconds"
    )
    revit_state: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Relevant Revit state after execution"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Execution timestamp"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "output": "Wall created successfully",
                "execution_time": 0.245,
                "timestamp": "2024-01-09T12:00:00Z"
            }
        }