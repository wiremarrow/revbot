"""
Test script that writes output to a file instead of stdout.
This works around the journal file issue.
"""
import os
import datetime

# Write to a file in temp directory
output_file = os.path.join(os.environ.get('TEMP', '.'), 'revbot_test_output.txt')

with open(output_file, 'w') as f:
    f.write("Hello from pyRevit!\n")
    f.write(f"Timestamp: {datetime.datetime.now()}\n")
    f.write("If you see this, pyRevit execution is working!\n")
    
    # Try to get Revit info
    try:
        doc = __revit__.ActiveUIDocument.Document
        f.write(f"Document Title: {doc.Title}\n")
        f.write(f"Revit Version: {__revit__.Application.VersionNumber}\n")
    except:
        f.write("Could not access Revit document info\n")

print(f"Output written to: {output_file}")

# Also try to return result via pyRevit's script module
try:
    from pyrevit import script
    output = script.get_output()
    output.print_md(f"**Success!** Output written to: `{output_file}`")
except:
    pass