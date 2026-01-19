#!/usr/bin/env python3
"""SAPA Speaker Tracker MCP Server.

An MCP server for managing the SAPA Data Science community speaker database via Notion.
"""

import os
import sys
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from sapa_speaker_tracker import (
    NotionSpeakerClient,
    SpeakerCreate,
    SpeakerUpdate,
    ContactStatus,
    Priority,
    FieldSpecialty,
)

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("SAPA Speaker Tracker")

# Initialize Notion client (lazy loading to allow env vars to be set)
_notion_client: Optional[NotionSpeakerClient] = None


def get_notion_client() -> NotionSpeakerClient:
    """Get or create the Notion client."""
    global _notion_client
    if _notion_client is None:
        _notion_client = NotionSpeakerClient()
    return _notion_client


@mcp.tool()
def add_speaker(
    name: str,
    field_specialty: Optional[str] = None,
    affiliation: Optional[str] = None,
    position: Optional[str] = None,
    linkedin_url: Optional[str] = None,
    potential_topics: Optional[list[str]] = None,
    contact_status: str = "Not Contacted",
    research_notes: Optional[str] = None,
    email: Optional[str] = None,
    priority: Optional[str] = None,
) -> str:
    """Add a new speaker to the SAPA speaker database.

    Args:
        name: Speaker's full name (required)
        field_specialty: Primary field - one of: "Drug Discovery & AI", "Clinical/Medical AI",
            "Genomics & Biotech", "Healthcare AI/ML", "Regulatory Science", "Real World Data/Evidence",
            "Bioinformatics", "Medical Imaging AI", "NLP in Healthcare", "Other"
        affiliation: University or company name
        position: Job title
        linkedin_url: LinkedIn profile URL
        potential_topics: List of topics they could speak on
        contact_status: Status - one of: "Not Contacted", "Contacted", "In Discussion",
            "Confirmed", "Declined", "Maybe Later", "No Response"
        research_notes: Bio summary and research findings
        email: Contact email address
        priority: Priority level - one of: "High", "Medium", "Low"

    Returns:
        Confirmation message with the new speaker's Notion page ID.
    """
    try:
        # Parse enums
        field_enum = None
        if field_specialty:
            try:
                field_enum = FieldSpecialty(field_specialty)
            except ValueError:
                return f"Error: Invalid field_specialty '{field_specialty}'. Valid options: {[f.value for f in FieldSpecialty]}"

        status_enum = ContactStatus.NOT_CONTACTED
        try:
            status_enum = ContactStatus(contact_status)
        except ValueError:
            return f"Error: Invalid contact_status '{contact_status}'. Valid options: {[s.value for s in ContactStatus]}"

        priority_enum = None
        if priority:
            try:
                priority_enum = Priority(priority)
            except ValueError:
                return f"Error: Invalid priority '{priority}'. Valid options: {[p.value for p in Priority]}"

        speaker = SpeakerCreate(
            name=name,
            field_specialty=field_enum,
            affiliation=affiliation,
            position=position,
            linkedin_url=linkedin_url,
            potential_topics=potential_topics or [],
            contact_status=status_enum,
            research_notes=research_notes,
            email=email,
            priority=priority_enum,
        )

        client = get_notion_client()
        result = client.add_speaker(speaker)

        return f"Successfully added speaker '{result.name}' to the database.\nNotion Page ID: {result.id}\nURL: {result.url}"

    except Exception as e:
        return f"Error adding speaker: {str(e)}"


@mcp.tool()
def search_speakers(
    name: Optional[str] = None,
    field_specialty: Optional[str] = None,
    affiliation: Optional[str] = None,
    contact_status: Optional[str] = None,
    priority: Optional[str] = None,
) -> str:
    """Search for speakers in the database with optional filters.

    Args:
        name: Filter by name (partial match)
        field_specialty: Filter by field/specialty
        affiliation: Filter by affiliation (partial match)
        contact_status: Filter by contact status
        priority: Filter by priority level

    Returns:
        List of matching speakers with their details.
    """
    try:
        # Parse enums
        field_enum = None
        if field_specialty:
            try:
                field_enum = FieldSpecialty(field_specialty)
            except ValueError:
                return f"Error: Invalid field_specialty. Valid options: {[f.value for f in FieldSpecialty]}"

        status_enum = None
        if contact_status:
            try:
                status_enum = ContactStatus(contact_status)
            except ValueError:
                return f"Error: Invalid contact_status. Valid options: {[s.value for s in ContactStatus]}"

        priority_enum = None
        if priority:
            try:
                priority_enum = Priority(priority)
            except ValueError:
                return f"Error: Invalid priority. Valid options: {[p.value for p in Priority]}"

        client = get_notion_client()
        speakers = client.search_speakers(
            name=name,
            field_specialty=field_enum,
            affiliation=affiliation,
            contact_status=status_enum,
            priority=priority_enum,
        )

        if not speakers:
            return "No speakers found matching the criteria."

        result_lines = [f"Found {len(speakers)} speaker(s):\n"]
        for s in speakers:
            result_lines.append(f"---")
            result_lines.append(f"Name: {s.name}")
            result_lines.append(f"ID: {s.id}")
            if s.field_specialty:
                result_lines.append(f"Field: {s.field_specialty.value}")
            if s.affiliation:
                result_lines.append(f"Affiliation: {s.affiliation}")
            if s.position:
                result_lines.append(f"Position: {s.position}")
            result_lines.append(f"Status: {s.contact_status.value}")
            if s.priority:
                result_lines.append(f"Priority: {s.priority.value}")
            if s.email:
                result_lines.append(f"Email: {s.email}")

        return "\n".join(result_lines)

    except Exception as e:
        return f"Error searching speakers: {str(e)}"


@mcp.tool()
def update_speaker(
    speaker_id: str,
    name: Optional[str] = None,
    field_specialty: Optional[str] = None,
    affiliation: Optional[str] = None,
    position: Optional[str] = None,
    linkedin_url: Optional[str] = None,
    potential_topics: Optional[list[str]] = None,
    contact_status: Optional[str] = None,
    research_notes: Optional[str] = None,
    email: Optional[str] = None,
    priority: Optional[str] = None,
) -> str:
    """Update an existing speaker's information.

    Args:
        speaker_id: The Notion page ID of the speaker to update (required)
        name: New name
        field_specialty: New field/specialty
        affiliation: New affiliation
        position: New position
        linkedin_url: New LinkedIn URL
        potential_topics: New list of potential topics
        contact_status: New contact status
        research_notes: New research notes
        email: New email
        priority: New priority level

    Returns:
        Confirmation message with updated speaker details.
    """
    try:
        # Parse enums
        field_enum = None
        if field_specialty:
            try:
                field_enum = FieldSpecialty(field_specialty)
            except ValueError:
                return f"Error: Invalid field_specialty. Valid options: {[f.value for f in FieldSpecialty]}"

        status_enum = None
        if contact_status:
            try:
                status_enum = ContactStatus(contact_status)
            except ValueError:
                return f"Error: Invalid contact_status. Valid options: {[s.value for s in ContactStatus]}"

        priority_enum = None
        if priority:
            try:
                priority_enum = Priority(priority)
            except ValueError:
                return f"Error: Invalid priority. Valid options: {[p.value for p in Priority]}"

        updates = SpeakerUpdate(
            name=name,
            field_specialty=field_enum,
            affiliation=affiliation,
            position=position,
            linkedin_url=linkedin_url,
            potential_topics=potential_topics,
            contact_status=status_enum,
            research_notes=research_notes,
            email=email,
            priority=priority_enum,
        )

        client = get_notion_client()
        result = client.update_speaker(speaker_id, updates)

        return f"Successfully updated speaker '{result.name}'.\nNotion Page ID: {result.id}\nStatus: {result.contact_status.value}"

    except Exception as e:
        return f"Error updating speaker: {str(e)}"


@mcp.tool()
def list_speakers(limit: int = 50) -> str:
    """List all speakers in the database.

    Args:
        limit: Maximum number of speakers to return (default: 50)

    Returns:
        List of all speakers with summary information.
    """
    try:
        client = get_notion_client()
        speakers = client.list_speakers(limit=limit)

        if not speakers:
            return "No speakers in the database yet."

        result_lines = [f"Total speakers: {len(speakers)}\n"]

        # Group by status
        by_status = {}
        for s in speakers:
            status = s.contact_status.value
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(s)

        for status, speakers_in_status in by_status.items():
            result_lines.append(f"\n## {status} ({len(speakers_in_status)})")
            for s in speakers_in_status:
                line = f"- {s.name}"
                if s.affiliation:
                    line += f" ({s.affiliation})"
                if s.priority:
                    line += f" [{s.priority.value}]"
                result_lines.append(line)

        return "\n".join(result_lines)

    except Exception as e:
        return f"Error listing speakers: {str(e)}"


@mcp.tool()
def get_speaker_details(speaker_id: str) -> str:
    """Get full details of a specific speaker.

    Args:
        speaker_id: The Notion page ID of the speaker

    Returns:
        Complete speaker information.
    """
    try:
        client = get_notion_client()
        s = client.get_speaker(speaker_id)

        lines = [
            f"# {s.name}",
            f"",
            f"**Notion ID:** {s.id}",
            f"**Notion URL:** {s.url or 'N/A'}",
            f"",
            f"## Professional Info",
            f"- **Field/Specialty:** {s.field_specialty.value if s.field_specialty else 'Not specified'}",
            f"- **Affiliation:** {s.affiliation or 'Not specified'}",
            f"- **Position:** {s.position or 'Not specified'}",
            f"",
            f"## Contact",
            f"- **Email:** {s.email or 'Not specified'}",
            f"- **LinkedIn:** {s.linkedin_url or 'Not specified'}",
            f"- **Status:** {s.contact_status.value}",
            f"- **Priority:** {s.priority.value if s.priority else 'Not set'}",
            f"",
            f"## Potential Topics",
        ]

        if s.potential_topics:
            for topic in s.potential_topics:
                lines.append(f"- {topic}")
        else:
            lines.append("- None specified")

        lines.extend([
            f"",
            f"## Research Notes",
            s.research_notes or "No notes yet.",
        ])

        return "\n".join(lines)

    except Exception as e:
        return f"Error getting speaker details: {str(e)}"


@mcp.tool()
def prepare_research_summary(
    name: str,
    affiliation: str,
    position: str,
    field_specialty: str,
    background: str,
    notable_work: str,
    potential_topics: list[str],
    linkedin_url: Optional[str] = None,
    email: Optional[str] = None,
    priority_recommendation: str = "Medium",
) -> str:
    """Format web research results into a structured summary for review before adding to the database.

    Use this after researching a potential speaker to present findings to the user for approval.

    Args:
        name: Speaker's full name
        affiliation: University or company
        position: Job title
        field_specialty: Primary field (must match valid options)
        background: Brief biography and background summary
        notable_work: Key publications, projects, or achievements
        potential_topics: List of topics they could speak on
        linkedin_url: LinkedIn profile URL if found
        email: Contact email if found
        priority_recommendation: Suggested priority level

    Returns:
        Formatted research summary for user review.
    """
    summary = f"""
# Research Summary: {name}

## Professional Profile
- **Name:** {name}
- **Position:** {position}
- **Affiliation:** {affiliation}
- **Field:** {field_specialty}

## Background
{background}

## Notable Work & Achievements
{notable_work}

## Potential Speaking Topics
"""
    for topic in potential_topics:
        summary += f"- {topic}\n"

    summary += f"""
## Contact Information
- **LinkedIn:** {linkedin_url or 'Not found'}
- **Email:** {email or 'Not found'}

## Recommendation
- **Priority:** {priority_recommendation}

---
**To add this speaker, confirm and I will call the add_speaker tool with the above information.**
"""

    return summary


@mcp.tool()
def test_connection() -> str:
    """Test the connection to the Notion database.

    Returns:
        Connection status and database information.
    """
    try:
        client = get_notion_client()
        result = client.test_connection()

        if result["success"]:
            return f"Connection successful!\nDatabase: {result['database_title']}\nDatabase ID: {result['database_id']}"
        else:
            return f"Connection failed: {result['error']}"

    except Exception as e:
        return f"Connection error: {str(e)}"


if __name__ == "__main__":
    mcp.run()
