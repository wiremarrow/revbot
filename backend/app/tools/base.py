"""
Base class for tools.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
from ..models.tools import Tool


class BaseTool(ABC):
    """Base class for all tools available to Claude."""
    
    @property
    @abstractmethod
    def definition(self) -> Tool:
        """Return the tool definition."""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> None:
        """Validate tool parameters."""
        required_params = [
            param.name for param in self.definition.parameters 
            if param.required
        ]
        
        for param in required_params:
            if param not in parameters:
                raise ValueError(f"Missing required parameter: {param}")
    
    async def safe_execute(self, **kwargs) -> Any:
        """Execute with parameter validation."""
        self.validate_parameters(kwargs)
        return await self.execute(**kwargs)