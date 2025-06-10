"""
API routes for RevBot.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional

from ..models.requests import CodeGenerationRequest, ExecutionRequest
from ..models.responses import CodeGenerationResponse, ExecutionResponse, ExecutionStatus
from ..services.code_service import CodeService
from ..core.logging import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["revit"])

# Initialize service
code_service = CodeService()


@router.post("/generate", response_model=CodeGenerationResponse)
async def generate_code(request: CodeGenerationRequest):
    """
    Generate Revit API code based on natural language description.
    
    This endpoint uses Claude with tool support to generate appropriate
    Revit API code for the given task.
    """
    try:
        logger.info("Code generation request", prompt=request.prompt)
        
        result = await code_service.generate_code(
            prompt=request.prompt,
            context=request.context,
            conversation_history=request.conversation_history,
            temperature=request.temperature
        )
        
        return CodeGenerationResponse(**result)
        
    except Exception as e:
        logger.error("Code generation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute", response_model=ExecutionResponse)
async def execute_code(request: ExecutionRequest):
    """
    Execute Python code in Revit via pyRevit.
    
    This endpoint sends the code to Revit for execution and returns
    the results. Use with caution as this executes code in the Revit environment.
    """
    try:
        logger.info("Code execution request", code_length=len(request.code))
        
        result = await code_service.execute_code(
            code=request.code,
            safe_mode=request.safe_mode,
            timeout=request.timeout
        )
        
        return ExecutionResponse(**result)
        
    except Exception as e:
        logger.error("Code execution failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat_with_assistant(
    prompt: str,
    execute_code: bool = False,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Combined endpoint for chatting with the assistant.
    
    This can both generate code and optionally execute it in one request.
    """
    try:
        # Generate code first
        generation_result = await code_service.generate_code(prompt=prompt)
        
        response = {
            "code": generation_result["code"],
            "explanation": generation_result.get("explanation"),
            "tool_results": generation_result.get("tool_results", [])
        }
        
        # Optionally execute the generated code
        if execute_code and generation_result.get("code"):
            execution_result = await code_service.execute_code(
                code=generation_result["code"],
                safe_mode=True
            )
            response["execution"] = execution_result
        
        return response
        
    except Exception as e:
        logger.error("Chat request failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "RevBot Backend",
        "version": "1.0.0"
    }


@router.get("/tools")
async def list_available_tools():
    """List all tools available to Claude."""
    tools = code_service.get_available_tools()
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": [
                    {
                        "name": param.name,
                        "type": param.type,
                        "description": param.description,
                        "required": param.required,
                        "default": param.default
                    }
                    for param in tool.parameters
                ]
            }
            for tool in tools
        ]
    }