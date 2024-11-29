import os
from src.assistant.tools.helpers import tool_response

def usage():
    return {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Lists all files in a specified directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "The path of the directory to list files."
                    }
                },
                "required": ["directory"]
            },
            "context": "Tool to list files in a specified directory."
        }
    }

def execute(directory):
    try:
        files = os.listdir(directory)
        return {
            "status": "success",
            "message": {"files": files}
        }
    except Exception as e:
        return {
            "status": "error",
            "message": {"error": str(e)}
        }
