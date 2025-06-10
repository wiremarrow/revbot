"""
Request models for API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class CodeGenerationRequest(BaseModel):
    """Request model for code generation."""
    
    prompt: str = Field(..., description="User's request for Revit code")
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context (e.g., current selection, document info)"
    )
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Previous conversation messages"
    )
    temperature: Optional[float] = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Model temperature for generation"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Create a wall at coordinates (0,0,0) to (10,0,0)",
                "context": {"active_view": "Level 1"},
                "temperature": 0.2
            }
        }


class ExecutionRequest(BaseModel):
    """Request model for code execution."""
    
    code: str = Field(..., description="Python code to execute in Revit")
    safe_mode: bool = Field(
        default=True,
        description="Whether to run code in safe mode with validation"
    )
    timeout: Optional[int] = Field(
        default=30,
        description="Execution timeout in seconds"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "# Create a simple wall\\nprint('Hello from Revit!')",
                "safe_mode": True,
                "timeout": 30
            }
        }