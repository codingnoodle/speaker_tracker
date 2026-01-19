# SAPA Speaker Tracker

An MCP (Model Context Protocol) server for managing the SAPA Data Science community speaker database via Notion.

## Overview

This project provides a FastMCP server that integrates with Claude Code to manage a speaker tracking database in Notion. It enables speaker research, database management, and tracking of potential speakers for bi-monthly webinars.

## Features

- **Speaker Management**: Add, search, update, and list speakers
- **Notion Integration**: Full CRUD operations with Notion database
- **MCP Tools**: Accessible via Claude Code for seamless workflow
- **Data Validation**: Pydantic models ensure data integrity
- **Flexible Search**: Filter speakers by name, field, affiliation, status, and priority

## Project Structure

```
speaker_tracker/
├── server.py                      # Main MCP server
├── pyproject.toml                 # Project dependencies
├── test_notion.py                 # Connection test script
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
└── src/
    └── sapa_speaker_tracker/
        ├── __init__.py            # Package exports
        ├── models.py              # Pydantic data models
        └── notion_client.py       # Notion API wrapper
```

## Setup

### 1. Install Dependencies

```bash
uv sync
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
NOTION_API_KEY=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id
```

### 3. Set Up Notion Database

Create a Notion database with the following properties:

| Property | Type | Purpose |
|----------|------|---------|
| Name | Title | Speaker's full name |
| Field/Specialty | Select | Primary field/specialty |
| Affiliation | Text | University or company |
| Position | Text | Job title |
| LinkedIn URL | URL | Profile link |
| Potential Topics | Multi-select | Topics they could speak on |
| Contact Status | Select | Not Contacted, Contacted, etc. |
| Research Notes | Text | Bio summary and findings |
| Email | Email | Contact email |
| Priority | Select | High, Medium, Low |

### 4. Test Connection

```bash
uv run python test_notion.py
```

## Usage

### Running the MCP Server

The server is configured to run via `uv`:

```bash
uv run python server.py
```

### MCP Tools Available

- `add_speaker` - Add new speaker to database
- `search_speakers` - Query speakers with filters
- `update_speaker` - Update existing speaker information
- `list_speakers` - List all speakers
- `get_speaker_details` - Get full details of a speaker
- `prepare_research_summary` - Format research for review
- `test_connection` - Verify Notion connection

### Example: Adding a Speaker

```python
from sapa_speaker_tracker import NotionSpeakerClient, SpeakerCreate, FieldSpecialty, Priority, ContactStatus

client = NotionSpeakerClient()

speaker = SpeakerCreate(
    name="Dr. Jane Smith",
    affiliation="Stanford University",
    position="Professor of AI",
    field_specialty=FieldSpecialty.CLINICAL_MEDICAL_AI,
    priority=Priority.HIGH,
    contact_status=ContactStatus.NOT_CONTACTED,
    potential_topics=["AI in Clinical Practice", "Machine Learning for Healthcare"]
)

result = client.add_speaker(speaker)
print(f"Added: {result.name} - {result.id}")
```

## Development

### Code Structure

- **models.py**: Pydantic models for type safety and validation
- **notion_client.py**: Handles all Notion API interactions
- **server.py**: FastMCP server with tool definitions

### Testing

Run the connection test:
```bash
uv run python test_notion.py
```

## Dependencies

- `mcp[cli]>=1.6.0` - FastMCP framework
- `notion-client>=2.2.0` - Notion API client
- `pydantic>=2.5.0` - Data validation
- `python-dotenv>=1.0.0` - Environment configuration

## License

MIT

## Contributing

Contributions welcome! Please ensure code follows existing patterns and includes appropriate error handling.
