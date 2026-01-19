"""Notion API wrapper for SAPA Speaker Tracker."""

import os
from typing import Optional
import httpx
from notion_client import Client
from notion_client.errors import APIResponseError

from .models import (
    Speaker,
    SpeakerCreate,
    SpeakerUpdate,
    ContactStatus,
    Priority,
    FieldSpecialty,
)

NOTION_API_VERSION = "2022-06-28"


class NotionSpeakerClient:
    """Client for interacting with Notion Speakers database."""

    def __init__(self, api_key: Optional[str] = None, database_id: Optional[str] = None):
        """Initialize the Notion client.

        Args:
            api_key: Notion integration token. Defaults to NOTION_API_KEY env var.
            database_id: Notion database ID. Defaults to NOTION_DATABASE_ID env var.
        """
        self.api_key = api_key or os.getenv("NOTION_API_KEY")
        self.database_id = database_id or os.getenv("NOTION_DATABASE_ID")

        if not self.api_key:
            raise ValueError("NOTION_API_KEY is required")
        if not self.database_id:
            raise ValueError("NOTION_DATABASE_ID is required")

        self.client = Client(auth=self.api_key)
        self._http_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json",
        }

    def _query_database(self, filter_obj: Optional[dict] = None, page_size: int = 100, start_cursor: Optional[str] = None) -> dict:
        """Query the database using direct HTTP request (workaround for notion-client 2.7.0 bug)."""
        body = {}
        if filter_obj:
            body["filter"] = filter_obj
        if page_size:
            body["page_size"] = page_size
        if start_cursor:
            body["start_cursor"] = start_cursor

        response = httpx.post(
            f"https://api.notion.com/v1/databases/{self.database_id}/query",
            headers=self._http_headers,
            json=body,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()

    def _build_properties(self, speaker: SpeakerCreate | SpeakerUpdate) -> dict:
        """Convert speaker model to Notion properties."""
        properties = {}

        if speaker.name is not None:
            properties["Name"] = {"title": [{"text": {"content": speaker.name}}]}

        if speaker.field_specialty is not None:
            properties["Field/Specialty"] = {"select": {"name": speaker.field_specialty.value}}

        if speaker.affiliation is not None:
            properties["Affiliation"] = {"rich_text": [{"text": {"content": speaker.affiliation}}]}

        if speaker.position is not None:
            properties["Position"] = {"rich_text": [{"text": {"content": speaker.position}}]}

        if speaker.linkedin_url is not None:
            properties["LinkedIn URL"] = {"url": speaker.linkedin_url if speaker.linkedin_url else None}

        if speaker.potential_topics is not None:
            properties["Potential Topics"] = {
                "multi_select": [{"name": topic} for topic in speaker.potential_topics]
            }

        if speaker.contact_status is not None:
            properties["Contact Status"] = {"select": {"name": speaker.contact_status.value}}

        if speaker.research_notes is not None:
            properties["Research Notes"] = {"rich_text": [{"text": {"content": speaker.research_notes}}]}

        if speaker.email is not None:
            properties["Email"] = {"email": speaker.email if speaker.email else None}

        if speaker.priority is not None:
            properties["Priority"] = {"select": {"name": speaker.priority.value}}

        return properties

    def _parse_page(self, page: dict) -> Speaker:
        """Convert Notion page to Speaker model."""
        props = page["properties"]

        # Extract title (Name)
        name = ""
        if props.get("Name", {}).get("title"):
            name = props["Name"]["title"][0]["text"]["content"] if props["Name"]["title"] else ""

        # Extract select fields
        field_specialty = None
        if props.get("Field/Specialty", {}).get("select"):
            field_val = props["Field/Specialty"]["select"]["name"]
            try:
                field_specialty = FieldSpecialty(field_val)
            except ValueError:
                field_specialty = FieldSpecialty.OTHER

        contact_status = ContactStatus.NOT_CONTACTED
        if props.get("Contact Status", {}).get("select"):
            status_val = props["Contact Status"]["select"]["name"]
            try:
                contact_status = ContactStatus(status_val)
            except ValueError:
                contact_status = ContactStatus.NOT_CONTACTED

        priority = None
        if props.get("Priority", {}).get("select"):
            priority_val = props["Priority"]["select"]["name"]
            try:
                priority = Priority(priority_val)
            except ValueError:
                priority = None

        # Extract rich text fields
        affiliation = ""
        if props.get("Affiliation", {}).get("rich_text"):
            affiliation = props["Affiliation"]["rich_text"][0]["text"]["content"] if props["Affiliation"]["rich_text"] else ""

        position = ""
        if props.get("Position", {}).get("rich_text"):
            position = props["Position"]["rich_text"][0]["text"]["content"] if props["Position"]["rich_text"] else ""

        research_notes = ""
        if props.get("Research Notes", {}).get("rich_text"):
            research_notes = props["Research Notes"]["rich_text"][0]["text"]["content"] if props["Research Notes"]["rich_text"] else ""

        # Extract URL field
        linkedin_url = props.get("LinkedIn URL", {}).get("url")

        # Extract email field
        email = props.get("Email", {}).get("email")

        # Extract multi-select (potential topics)
        potential_topics = []
        if props.get("Potential Topics", {}).get("multi_select"):
            potential_topics = [item["name"] for item in props["Potential Topics"]["multi_select"]]

        return Speaker(
            id=page["id"],
            url=page.get("url"),
            name=name,
            field_specialty=field_specialty,
            affiliation=affiliation or None,
            position=position or None,
            linkedin_url=linkedin_url,
            potential_topics=potential_topics,
            contact_status=contact_status,
            research_notes=research_notes or None,
            email=email,
            priority=priority,
        )

    def add_speaker(self, speaker: SpeakerCreate) -> Speaker:
        """Add a new speaker to the database.

        Args:
            speaker: Speaker data to add.

        Returns:
            The created Speaker with Notion ID.
        """
        properties = self._build_properties(speaker)

        page = self.client.pages.create(
            parent={"database_id": self.database_id},
            properties=properties,
        )

        return self._parse_page(page)

    def get_speaker(self, page_id: str) -> Speaker:
        """Get a speaker by their Notion page ID.

        Args:
            page_id: The Notion page ID.

        Returns:
            The Speaker object.
        """
        page = self.client.pages.retrieve(page_id=page_id)
        return self._parse_page(page)

    def update_speaker(self, page_id: str, updates: SpeakerUpdate) -> Speaker:
        """Update a speaker's information.

        Args:
            page_id: The Notion page ID.
            updates: Fields to update.

        Returns:
            The updated Speaker object.
        """
        properties = self._build_properties(updates)

        if not properties:
            return self.get_speaker(page_id)

        page = self.client.pages.update(
            page_id=page_id,
            properties=properties,
        )

        return self._parse_page(page)

    def search_speakers(
        self,
        name: Optional[str] = None,
        field_specialty: Optional[FieldSpecialty] = None,
        affiliation: Optional[str] = None,
        contact_status: Optional[ContactStatus] = None,
        priority: Optional[Priority] = None,
    ) -> list[Speaker]:
        """Search speakers with filters.

        Args:
            name: Filter by name (contains).
            field_specialty: Filter by field/specialty.
            affiliation: Filter by affiliation (contains).
            contact_status: Filter by contact status.
            priority: Filter by priority level.

        Returns:
            List of matching Speaker objects.
        """
        filters = []

        if name:
            filters.append({
                "property": "Name",
                "title": {"contains": name}
            })

        if field_specialty:
            filters.append({
                "property": "Field/Specialty",
                "select": {"equals": field_specialty.value}
            })

        if affiliation:
            filters.append({
                "property": "Affiliation",
                "rich_text": {"contains": affiliation}
            })

        if contact_status:
            filters.append({
                "property": "Contact Status",
                "select": {"equals": contact_status.value}
            })

        if priority:
            filters.append({
                "property": "Priority",
                "select": {"equals": priority.value}
            })

        filter_obj = None
        if len(filters) == 1:
            filter_obj = filters[0]
        elif len(filters) > 1:
            filter_obj = {"and": filters}

        results = self._query_database(filter_obj=filter_obj)

        return [self._parse_page(page) for page in results["results"]]

    def list_speakers(self, limit: int = 100) -> list[Speaker]:
        """List all speakers in the database.

        Args:
            limit: Maximum number of speakers to return.

        Returns:
            List of Speaker objects.
        """
        results = self._query_database(page_size=min(limit, 100))

        speakers = [self._parse_page(page) for page in results["results"]]

        # Handle pagination if needed
        while results.get("has_more") and len(speakers) < limit:
            results = self._query_database(
                page_size=min(limit - len(speakers), 100),
                start_cursor=results["next_cursor"],
            )
            speakers.extend([self._parse_page(page) for page in results["results"]])

        return speakers[:limit]

    def delete_speaker(self, page_id: str) -> bool:
        """Archive (soft delete) a speaker.

        Args:
            page_id: The Notion page ID.

        Returns:
            True if successful.
        """
        self.client.pages.update(page_id=page_id, archived=True)
        return True

    def test_connection(self) -> dict:
        """Test the Notion connection and database access.

        Returns:
            Database info if successful.
        """
        try:
            db = self.client.databases.retrieve(database_id=self.database_id)
            return {
                "success": True,
                "database_title": db["title"][0]["text"]["content"] if db.get("title") else "Untitled",
                "database_id": self.database_id,
            }
        except APIResponseError as e:
            return {
                "success": False,
                "error": str(e),
            }
