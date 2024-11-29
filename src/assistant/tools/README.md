# Tools
Houses all the functions which can be invoked by an LLM or other means.

## Tool naming: `{my_descriptive_tool_name}`
Tools should be named descriptively as to provide additional context, is also relevant for parameter names, and static values.

## Tool dir (folder) content:
- `{my_descriptive_tool_name}.py`: This file implements the functionality of the function module, featuring two main functions:
    - `usage()`: Returns usage instruction (information on how to utilise the function).
    - `execute()`: Code required to carry out the function operations.
