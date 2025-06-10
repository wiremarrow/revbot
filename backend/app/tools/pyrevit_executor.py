"""
PyRevit script execution tool.
"""
import asyncio
import json
import time
from typing import Dict, Any, Optional
import aiofiles
import websockets
from pathlib import Path
import tempfile
import uuid

from ..models.tools import Tool, ToolParameter, ParameterType
from .base import BaseTool
from config.config import settings
import structlog

logger = structlog.get_logger(__name__)


class PyRevitExecutorTool(BaseTool):
    """Tool for executing Python scripts in Revit via pyRevit."""
    
    @property
    def definition(self) -> Tool:
        return Tool(
            name="execute_pyrevit_script",
            description="Execute a Python script in Revit using pyRevit. Use this to test generated code or perform actions in Revit.",
            parameters=[
                ToolParameter(
                    name="code",
                    type=ParameterType.STRING,
                    description="Python code to execute in Revit",
                    required=True
                ),
                ToolParameter(
                    name="timeout",
                    type=ParameterType.NUMBER,
                    description="Execution timeout in seconds",
                    required=False,
                    default=30
                ),
                ToolParameter(
                    name="capture_output",
                    type=ParameterType.BOOLEAN,
                    description="Whether to capture and return script output",
                    required=False,
                    default=True
                )
            ]
        )
    
    async def execute(
        self,
        code: str,
        timeout: int = 30,
        capture_output: bool = True
    ) -> Dict[str, Any]:
        """Execute Python code in Revit via pyRevit."""
        logger.info("Executing pyRevit script", code_length=len(code))
        
        start_time = time.time()
        
        try:
            # Validate the code first
            validation_result = self._validate_code(code)
            if not validation_result["is_valid"]:
                return {
                    "success": False,
                    "error": f"Code validation failed: {validation_result['error']}",
                    "execution_time": time.time() - start_time
                }
            
            # Prepare the script for execution
            prepared_code = self._prepare_code(code, capture_output)
            
            # Execute via pyRevit (two methods supported)
            if settings.pyrevit_port is not None and settings.pyrevit_port > 0:
                # Method 1: WebSocket communication with pyRevit server
                logger.info("Using WebSocket method", port=settings.pyrevit_port)
                result = await self._execute_via_websocket(prepared_code, timeout)
            else:
                # Method 2: File-based execution with pyRevit CLI
                logger.info("Using CLI method (WebSocket disabled)")
                result = await self._execute_via_cli(prepared_code, timeout)
            
            execution_time = time.time() - start_time
            
            return {
                "success": result.get("success", False),
                "output": result.get("output", ""),
                "error": result.get("error"),
                "execution_time": execution_time,
                "revit_state": result.get("revit_state", {})
            }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Script execution timed out after {timeout} seconds",
                "execution_time": timeout
            }
        except Exception as e:
            logger.error("Script execution failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    def _validate_code(self, code: str) -> Dict[str, Any]:
        """Validate Python code for safety and syntax."""
        # Basic syntax check
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            return {"is_valid": False, "error": f"Syntax error: {e}"}
        
        # Security checks - prevent dangerous operations
        dangerous_patterns = [
            "exec(",
            "eval(",
            "__import__",
            "open(",
            "file(",
            "input(",
            "raw_input(",
            "compile(",
            "globals(",
            "locals(",
            "vars(",
            "dir(",
        ]
        
        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                return {
                    "is_valid": False,
                    "error": f"Potentially dangerous operation detected: {pattern}"
                }
        
        return {"is_valid": True}
    
    def _prepare_code(self, code: str, capture_output: bool) -> str:
        """Prepare code for execution with necessary wrappers."""
        if capture_output:
            # Wrap code to capture output
            wrapped_code = f"""
import sys
from io import StringIO
import json

# Capture output
output_buffer = StringIO()
error_buffer = StringIO()
old_stdout = sys.stdout
old_stderr = sys.stderr

result = {{"success": True, "output": "", "error": None, "revit_state": {{}}}}

try:
    sys.stdout = output_buffer
    sys.stderr = error_buffer
    
    # User code execution
{self._indent_code(code)}
    
    # Capture Revit state if possible
    try:
        result["revit_state"] = {{
            "active_view": str(doc.ActiveView.Name) if 'doc' in locals() else None,
            "selection_count": uidoc.Selection.GetElementIds().Count if 'uidoc' in locals() else 0
        }}
    except:
        pass
    
    result["output"] = output_buffer.getvalue()
    
except Exception as e:
    result["success"] = False
    result["error"] = str(e)
    result["output"] = output_buffer.getvalue()
    
finally:
    sys.stdout = old_stdout
    sys.stderr = old_stderr

# Output result as JSON for parsing
print("===REVITAI_RESULT_START===")
print(json.dumps(result))
print("===REVITAI_RESULT_END===")
"""
            return wrapped_code
        else:
            # Simple execution without output capture
            return code
    
    async def _execute_via_websocket(self, code: str, timeout: int) -> Dict[str, Any]:
        """Execute code via WebSocket connection to pyRevit."""
        ws_url = f"ws://localhost:{settings.pyrevit_port}/revitai"
        
        try:
            async with websockets.connect(ws_url) as websocket:
                # Send execution request
                request = {
                    "action": "execute",
                    "code": code,
                    "id": str(uuid.uuid4())
                }
                
                await websocket.send(json.dumps(request))
                
                # Wait for response with timeout
                response_text = await asyncio.wait_for(
                    websocket.recv(),
                    timeout=timeout
                )
                
                response = json.loads(response_text)
                
                # Parse the output if it contains our result markers
                if "output" in response and "===REVITAI_RESULT_START===" in response["output"]:
                    return self._parse_wrapped_output(response["output"])
                
                return response
                
        except (websockets.exceptions.WebSocketException, ConnectionRefusedError) as e:
            logger.warning("WebSocket connection failed, falling back to CLI", error=str(e))
            # Fall back to CLI execution
            return await self._execute_via_cli(code, timeout)
    
    async def _execute_via_cli(self, code: str, timeout: int) -> Dict[str, Any]:
        """Execute code via pyRevit CLI (file-based)."""
        
        # First check if pyRevit CLI is available
        try:
            check_process = await asyncio.create_subprocess_exec(
                'pyrevit',
                '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await check_process.communicate()
            if check_process.returncode != 0:
                return {
                    "success": False,
                    "output": "",
                    "error": "pyRevit CLI not found or not working. Install pyRevit and ensure it's in PATH.",
                    "revit_state": {}
                }
            logger.info("pyRevit CLI found", version=stdout.decode('utf-8').strip())
        except FileNotFoundError:
            return {
                "success": False,
                "output": "",
                "error": "pyRevit CLI not found. Install pyRevit and ensure 'pyrevit' command is in PATH.",
                "revit_state": {}
            }
        
        # Create a temporary script file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
            dir=self._get_pyrevit_scripts_dir()
        ) as f:
            f.write(code)
            script_path = f.name
        
        try:
            # Execute using pyrevit run command
            logger.info("Executing pyRevit CLI", script_path=script_path)
            
            process = await asyncio.create_subprocess_exec(
                'pyrevit',
                'run',
                script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            output = stdout.decode('utf-8')
            error = stderr.decode('utf-8') if stderr else None
            
            logger.info(
                "pyRevit CLI execution completed",
                return_code=process.returncode,
                stdout_length=len(output),
                stderr_length=len(error) if error else 0
            )
            
            # Parse the output
            if "===REVITAI_RESULT_START===" in output:
                return self._parse_wrapped_output(output)
            
            # If no output and immediate failure, likely Revit connection issue
            if process.returncode != 0 and not output and not error:
                return {
                    "success": False,
                    "output": f"DEBUG: No output from pyRevit. Return code: {process.returncode}",
                    "error": f"pyRevit executed but no response from Revit. Return code: {process.returncode}. Check: 1) Revit is running, 2) pyRevit is loaded in Revit, 3) A document is open in Revit",
                    "revit_state": {},
                    "debug_info": {
                        "return_code": process.returncode,
                        "execution_time": f"~0.0003s (immediate failure)",
                        "script_path": script_path,
                        "pyrevit_command": f"pyrevit run {script_path}"
                    }
                }
            
            return {
                "success": process.returncode == 0,
                "output": output if output else f"DEBUG: Empty output. Return code: {process.returncode}",
                "error": error if error else f"No stderr. Return code: {process.returncode}",
                "revit_state": {},
                "debug_info": {
                    "return_code": process.returncode,
                    "script_path": script_path,
                    "pyrevit_command": f"pyrevit run {script_path}",
                    "stdout_length": len(output),
                    "stderr_length": len(error) if error else 0
                }
            }
            
        finally:
            # Clean up temporary file
            Path(script_path).unlink(missing_ok=True)
    
    def _parse_wrapped_output(self, output: str) -> Dict[str, Any]:
        """Parse output from wrapped code execution."""
        try:
            start_marker = "===REVITAI_RESULT_START==="
            end_marker = "===REVITAI_RESULT_END==="
            
            start_idx = output.find(start_marker) + len(start_marker)
            end_idx = output.find(end_marker)
            
            if start_idx > len(start_marker) - 1 and end_idx > start_idx:
                result_json = output[start_idx:end_idx].strip()
                return json.loads(result_json)
            
            # Fallback if markers not found
            return {
                "success": True,
                "output": output,
                "error": None,
                "revit_state": {}
            }
            
        except Exception as e:
            logger.error("Failed to parse wrapped output", error=str(e))
            return {
                "success": False,
                "output": output,
                "error": f"Output parsing failed: {str(e)}",
                "revit_state": {}
            }
    
    def _get_pyrevit_scripts_dir(self) -> Path:
        """Get pyRevit scripts directory for temporary files."""
        # Default location - can be configured
        scripts_dir = Path.home() / ".pyrevit" / "scripts" / "revitai_temp"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        return scripts_dir
    
    def _indent_code(self, code: str, spaces: int = 4) -> str:
        """Indent code by specified number of spaces."""
        indent = " " * spaces
        return "\n".join(indent + line for line in code.split("\n"))