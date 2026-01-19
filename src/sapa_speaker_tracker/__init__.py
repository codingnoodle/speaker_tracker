"""SAPA Speaker Tracker - MCP server for managing speaker database via Notion."""

from .models import Speaker, SpeakerCreate, SpeakerUpdate, ContactStatus, Priority, FieldSpecialty
from .notion_client import NotionSpeakerClient

__all__ = [
    "Speaker",
    "SpeakerCreate",
    "SpeakerUpdate",
    "ContactStatus",
    "Priority",
    "FieldSpecialty",
    "NotionSpeakerClient",
]
