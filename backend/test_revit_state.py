"""
Test script that checks Revit state and writes results.
This helps debug the RevBot integration.
"""
import sys
import json
import os

# Output file for results
output_file = os.path.join(os.environ.get('TEMP', '.'), 'revbot_state.json')

result = {
    "success": False,
    "message": "Starting test",
    "revit_info": {},
    "errors": []
}

try:
    # Check if we're in pyRevit environment
    if '__revit__' in globals():
        result["revit_info"]["has_revit"] = True
        result["revit_info"]["version"] = str(__revit__.Application.VersionNumber)
        
        # Check for active document
        doc = __revit__.ActiveUIDocument.Document
        if doc:
            result["revit_info"]["document_title"] = doc.Title
            result["revit_info"]["document_path"] = doc.PathName
            result["success"] = True
            result["message"] = "Successfully accessed Revit document"
        else:
            result["message"] = "No active document"
    else:
        result["message"] = "__revit__ not found in globals"
        result["errors"].append("Not running in pyRevit environment")
        
except Exception as e:
    result["errors"].append(str(e))
    result["message"] = f"Error: {str(e)}"

# Write results
with open(output_file, 'w') as f:
    json.dump(result, f, indent=2)

# Also try stdout (might work in some configurations)
print(f"REVBOT_RESULT_JSON:{json.dumps(result)}")