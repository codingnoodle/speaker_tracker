# How MCP Works in This Project

## What is MCP?

**MCP (Model Context Protocol)** is a protocol that allows AI assistants (like Claude) to interact with external tools and data sources. Think of it as a bridge between Claude and your applications.

## Architecture Overview

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│ Claude Code │ ◄─────► │  MCP Server  │ ◄─────► │   Notion    │
│  (Client)   │  JSON   │  (server.py) │  API    │  Database   │
└─────────────┘         └──────────────┘         └─────────────┘
```

1. **Claude Code** (the AI) sends requests to the MCP server
2. **MCP Server** processes the request and calls your Python functions
3. **Notion API** is used to interact with your database
4. Results flow back through the chain

## How It Works in This Project

### 1. MCP Server Initialization

```python
# server.py, line 30
mcp = FastMCP("SAPA Speaker Tracker")
```

This creates an MCP server instance. `FastMCP` is a framework that makes it easy to create MCP servers.

### 2. Tool Registration

Tools are registered using the `@mcp.tool()` decorator:

```python
@mcp.tool()
def add_speaker(
    name: str,
    affiliation: Optional[str] = None,
    # ... other parameters
) -> str:
    """Add a new speaker to the database."""
    # Function implementation
    return "Successfully added..."
```

**What happens:**
- The decorator automatically:
  - Extracts the function signature
  - Reads the docstring for tool description
  - Converts Python types to MCP tool schema
  - Registers it as an available tool

### 3. Tool Execution Flow

When you ask Claude to "add a speaker", here's what happens:

```
1. You: "Add Dr. Jane Smith from Stanford as a speaker"
   ↓
2. Claude Code recognizes this needs the add_speaker tool
   ↓
3. Claude sends JSON-RPC request to MCP server:
   {
     "method": "tools/call",
     "params": {
       "name": "add_speaker",
       "arguments": {
         "name": "Dr. Jane Smith",
         "affiliation": "Stanford University"
       }
     }
   }
   ↓
4. MCP server receives request and calls your Python function
   ↓
5. Your function executes:
   - Validates input
   - Creates SpeakerCreate object
   - Calls Notion API via NotionSpeakerClient
   - Returns result
   ↓
6. MCP server sends response back to Claude:
   {
     "result": "Successfully added speaker 'Dr. Jane Smith'..."
   }
   ↓
7. Claude presents the result to you
```

## Key Components

### FastMCP Framework

```python
from mcp.server.fastmcp import FastMCP
```

**FastMCP** simplifies MCP server creation:
- Handles JSON-RPC protocol automatically
- Converts Python functions to MCP tools
- Manages tool registration and discovery
- Handles stdin/stdout communication

### Tool Decorator

```python
@mcp.tool()
```

This decorator:
- **Registers** the function as an MCP tool
- **Extracts** parameter types from function signature
- **Generates** tool schema from docstring
- **Makes** the tool available to Claude

### Tool Parameters

MCP automatically converts Python types to tool schemas:

```python
def add_speaker(
    name: str,                          # Required string
    affiliation: Optional[str] = None,  # Optional string
    potential_topics: Optional[list[str]] = None,  # Optional list
    priority: Optional[str] = None      # Optional string
) -> str:                               # Returns string
```

Becomes an MCP tool with:
- `name`: required string parameter
- `affiliation`: optional string parameter
- `potential_topics`: optional array parameter
- `priority`: optional string parameter

## Available Tools in This Project

### 1. `add_speaker`
**Purpose**: Add a new speaker to the Notion database

**Flow**:
```
User request → MCP tool → Validate input → Create Pydantic model → 
Notion API call → Create page → Return confirmation
```

### 2. `search_speakers`
**Purpose**: Find speakers matching criteria

**Flow**:
```
User query → MCP tool → Build filter → Notion API query → 
Parse results → Format response → Return to Claude
```

### 3. `update_speaker`
**Purpose**: Update existing speaker information

**Flow**:
```
User request → MCP tool → Validate updates → Notion API update → 
Return confirmation
```

### 4. `list_speakers`
**Purpose**: List all speakers, optionally grouped

**Flow**:
```
User request → MCP tool → Notion API query → Group by status → 
Format list → Return to Claude
```

### 5. `get_speaker_details`
**Purpose**: Get complete information about one speaker

**Flow**:
```
User request → MCP tool → Notion API get → Format details → 
Return formatted text
```

### 6. `prepare_research_summary`
**Purpose**: Format research findings for review

**Flow**:
```
Research data → MCP tool → Format markdown → Return summary
```

### 7. `test_connection`
**Purpose**: Verify Notion connection works

**Flow**:
```
User request → MCP tool → Notion API test → Return status
```

## How Claude Code Connects

### Configuration

In your Cursor/Claude Code settings (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "sapa-speakers": {
      "command": "uv",
      "args": [
        "--directory", 
        "/path/to/speaker_tracker",
        "run", 
        "python", 
        "server.py"
      ],
      "env": {
        "NOTION_API_KEY": "your_token",
        "NOTION_DATABASE_ID": "your_database_id"
      }
    }
  }
}
```

**What this does:**
1. Claude Code starts the MCP server as a subprocess
2. Server runs `uv run python server.py`
3. Server communicates via stdin/stdout (JSON-RPC)
4. Claude Code discovers available tools
5. You can now use the tools in conversations

## Communication Protocol

MCP uses **JSON-RPC 2.0** over stdin/stdout:

### Request Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "add_speaker",
    "arguments": {
      "name": "Dr. Jane Smith",
      "affiliation": "Stanford"
    }
  }
}
```

### Response Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Successfully added speaker 'Dr. Jane Smith'..."
      }
    ]
  }
}
```

## Error Handling

Each tool has try-except blocks:

```python
@mcp.tool()
def add_speaker(...) -> str:
    try:
        # Do work
        return "Success message"
    except Exception as e:
        return f"Error: {str(e)}"
```

Errors are returned as strings, which Claude can interpret and explain to you.

## Benefits of This Architecture

1. **Separation of Concerns**
   - Business logic in Python functions
   - MCP handles protocol communication
   - Notion client handles API details

2. **Type Safety**
   - Pydantic models validate data
   - Type hints help catch errors
   - Enum types ensure valid values

3. **Easy to Extend**
   - Add new tools by adding new `@mcp.tool()` functions
   - No need to modify protocol code
   - FastMCP handles everything

4. **Natural Language Interface**
   - You talk to Claude in plain English
   - Claude translates to tool calls
   - Results come back in readable format

## Example: Complete Flow

**You say**: "Add Dr. Sarah Chen from MIT as a speaker, she's in Clinical/Medical AI"

**What happens**:

1. Claude recognizes this needs `add_speaker`
2. Claude calls: `add_speaker(name="Dr. Sarah Chen", affiliation="MIT", field_specialty="Clinical/Medical AI")`
3. MCP server receives the call
4. Function validates and creates `SpeakerCreate` object
5. `NotionSpeakerClient.add_speaker()` is called
6. Notion API creates a new page
7. Response: "Successfully added speaker 'Dr. Sarah Chen'..."
8. Claude tells you: "I've added Dr. Sarah Chen to your database!"

## Key Takeaways

- **MCP** = Protocol for AI to use tools
- **FastMCP** = Framework that makes it easy
- **@mcp.tool()** = Decorator that registers functions as tools
- **JSON-RPC** = Communication protocol (handled automatically)
- **Your functions** = The actual work happens here
- **Notion API** = Where data is stored/retrieved

The beauty is: **You write normal Python functions, and they automatically become AI-accessible tools!**
