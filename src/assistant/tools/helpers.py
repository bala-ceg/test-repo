from datetime import datetime
import os
import sys
import importlib
import logging
import requests


# Helper functions for common operations

def list_tool_directories(tools_path):
    """List all tool directories in the tools directory."""
    return [d for d in os.listdir(tools_path) if os.path.isdir(os.path.join(tools_path, d))]

def load_tool(tool_name):
    """Load the command module for a given tool."""
    module_name = f"{tool_name}.{tool_name}"
    if module_name in sys.modules:
        logging.info(f"Reloading {module_name}")
        importlib.reload(sys.modules[module_name])
    else:
        logging.info(f"Importing {module_name}")
        importlib.import_module(module_name)


def bootstrap_tools(tools_path, whitelist=None, blacklist=None):
    # Get all the tool directories
    tool_directories = list_tool_directories(tools_path=tools_path)

    # Strip out any dir with prefix with a `.` or `_`
    tool_directories = [d for d in tool_directories if not d.startswith(('.', '_'))]

    # Filter out the filtered tool directories
    if whitelist:
        tool_directories = [d for d in tool_directories if d in whitelist]
    
    if blacklist:
        tool_directories = [d for d in tool_directories if d not in blacklist]

    logging.info(f"Default Tools: {tool_directories}")


    # Load the config for each tool
    for tool_name in tool_directories:
        load_tool(tool_name)

    # Create a dict of each tools usage function(s)
    definitions = []
    for tool_name in tool_directories:
        try:
            command = sys.modules[f"{tool_name}.{tool_name}"]
            definitions.append(command.usage())
        except Exception as e:
            logging.error(f"Error loading command: {e}")
    
    return {
        "definitions": definitions,
        "tools": tool_directories
    }



def tool_response(status, message):
    return {
        "status": status,
        "message": message
    }

def is_valid_datetime(datetime_str):
    try:
        datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        # Test date is in the future or not (small margin error here, if run at 5AM, it will fail, but that's okay for this test case.)
        if datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S') < datetime.now():
            return False
        return True
    except ValueError:
        return False

def is_valid_config(config, required_config_keys):
    for key in required_config_keys:
        if key not in config:
            return False
        if not config[key]:
            return False
    return True


def valid_toolset(toolset):
    if not toolset:
        raise ValueError("No toolset provided to get model response")
    
    # check toolset has definitions and tools
    if 'definitions' not in toolset:
        logging.error(toolset)
        raise ValueError("Toolset must contain definitions")
    
    if 'tools' not in toolset:
        raise ValueError("Toolset must contain tools")
    
    if not isinstance(toolset, dict):
        raise ValueError("Toolset must be a dictionary")
    

def get_request_session():
    session = requests.Session()
    # Set the User-Agent header to identify the request
    session.headers.update({'User-Agent': 'My Assistant'})
    # Set requests default timeout to 10 seconds
    session.timeout = 10
    return session