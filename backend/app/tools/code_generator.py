"""
Code generation tool for Revit API.
"""
from typing import Dict, Any
from ..models.tools import Tool, ToolParameter, ParameterType
from .base import BaseTool
import structlog

logger = structlog.get_logger(__name__)


class CodeGeneratorTool(BaseTool):
    """Tool for generating Revit API code based on descriptions."""
    
    @property
    def definition(self) -> Tool:
        return Tool(
            name="generate_revit_code",
            description="Generate Revit API Python code based on a natural language description of what to accomplish",
            parameters=[
                ToolParameter(
                    name="description",
                    type=ParameterType.STRING,
                    description="Natural language description of what the code should do",
                    required=True
                ),
                ToolParameter(
                    name="context",
                    type=ParameterType.OBJECT,
                    description="Additional context about the Revit environment (e.g., selected elements, active view)",
                    required=False
                ),
                ToolParameter(
                    name="include_imports",
                    type=ParameterType.BOOLEAN,
                    description="Whether to include all necessary import statements",
                    required=False,
                    default=True
                ),
                ToolParameter(
                    name="include_transaction",
                    type=ParameterType.BOOLEAN,
                    description="Whether to wrap code in a Revit transaction",
                    required=False,
                    default=True
                )
            ]
        )
    
    async def execute(
        self,
        description: str,
        context: Dict[str, Any] = None,
        include_imports: bool = True,
        include_transaction: bool = True
    ) -> Dict[str, Any]:
        """Generate Revit API code based on description."""
        logger.info("Generating Revit code", description=description)
        
        try:
            # Build code template
            code_parts = []
            
            if include_imports:
                imports = self._generate_imports(description, context)
                code_parts.append(imports)
            
            # Generate main code
            main_code = self._generate_main_code(description, context)
            
            if include_transaction:
                transaction_code = self._wrap_in_transaction(main_code, description)
                code_parts.append(transaction_code)
            else:
                code_parts.append(main_code)
            
            generated_code = "\n\n".join(code_parts)
            
            return {
                "code": generated_code,
                "explanation": self._generate_explanation(description),
                "warnings": self._check_for_warnings(description, context)
            }
            
        except Exception as e:
            logger.error("Code generation failed", error=str(e))
            raise
    
    def _generate_imports(self, description: str, context: Dict[str, Any] = None) -> str:
        """Generate appropriate import statements."""
        # Basic imports that are almost always needed
        imports = [
            "import clr",
            "clr.AddReference('RevitAPI')",
            "clr.AddReference('RevitAPIUI')",
            "",
            "from Autodesk.Revit.DB import *",
            "from Autodesk.Revit.UI import *",
            "from Autodesk.Revit.DB.Architecture import *",
            "from Autodesk.Revit.DB.Structure import *",
            "",
            "# pyRevit imports",
            "from pyrevit import revit, DB, UI",
            "from pyrevit import script",
            "",
            "# Get current document and application",
            "doc = __revit__.ActiveUIDocument.Document",
            "uidoc = __revit__.ActiveUIDocument",
            "app = __revit__.Application"
        ]
        
        # Add specific imports based on keywords in description
        description_lower = description.lower()
        
        if "family" in description_lower:
            imports.append("from Autodesk.Revit.DB import FamilyInstance, Family")
        
        if "parameter" in description_lower:
            imports.append("from Autodesk.Revit.DB import ParameterFilterElement, ParameterFilterRuleFactory")
        
        if "view" in description_lower:
            imports.append("from Autodesk.Revit.DB import ViewPlan, ViewSection, View3D")
        
        if "sheet" in description_lower:
            imports.append("from Autodesk.Revit.DB import ViewSheet")
        
        return "\n".join(imports)
    
    def _generate_main_code(self, description: str, context: Dict[str, Any] = None) -> str:
        """Generate the main code logic."""
        # This is a simplified version - in reality, this would use more sophisticated
        # code generation based on the description
        code_template = """# Main code logic
# TODO: This is a template - actual implementation would be based on the description
# Description: {description}

# Get current selection or use active view
selection = uidoc.Selection
selected_ids = selection.GetElementIds()

if selected_ids.Count > 0:
    # Work with selected elements
    elements = [doc.GetElement(id) for id in selected_ids]
    print(f"Working with {{len(elements)}} selected elements")
else:
    # Work with all elements in active view
    collector = FilteredElementCollector(doc, doc.ActiveView.Id)
    elements = collector.WhereElementIsNotElementType().ToElements()
    print(f"Working with {{len(elements)}} elements in active view")

# Your code implementation here based on: {description}"""
        
        return code_template.format(description=description)
    
    def _wrap_in_transaction(self, code: str, description: str) -> str:
        """Wrap code in a Revit transaction."""
        # Create a transaction name from the description
        trans_name = description[:50] if len(description) > 50 else description
        
        wrapped = f"""# Create and execute transaction
t = Transaction(doc, "{trans_name}")
try:
    t.Start()
    
{self._indent_code(code)}
    
    t.Commit()
    print("Transaction completed successfully")
except Exception as e:
    t.RollBack()
    print(f"Error: {{str(e)}}")
    raise"""
        
        return wrapped
    
    def _indent_code(self, code: str, spaces: int = 4) -> str:
        """Indent code by specified number of spaces."""
        indent = " " * spaces
        return "\n".join(indent + line for line in code.split("\n"))
    
    def _generate_explanation(self, description: str) -> str:
        """Generate explanation of what the code does."""
        return f"This code implements: {description}"
    
    def _check_for_warnings(self, description: str, context: Dict[str, Any] = None) -> list:
        """Check for potential issues or warnings."""
        warnings = []
        
        description_lower = description.lower()
        
        if "delete" in description_lower or "remove" in description_lower:
            warnings.append("This operation will permanently modify the model. Ensure you have a backup.")
        
        if "all" in description_lower and "element" in description_lower:
            warnings.append("Operating on all elements may be slow for large models.")
        
        if context and context.get("is_workshared"):
            warnings.append("This is a workshared model. Ensure you have proper permissions.")
        
        return warnings if warnings else None