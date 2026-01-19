"""Pydantic models for SAPA Speaker Tracker."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, EmailStr


class FieldSpecialty(str, Enum):
    """Speaker field/specialty options."""
    DRUG_DISCOVERY_AI = "Drug Discovery & AI"
    CLINICAL_MEDICAL_AI = "Clinical/Medical AI"
    GENOMICS_BIOTECH = "Genomics & Biotech"
    HEALTHCARE_AI_ML = "Healthcare AI/ML"
    REGULATORY_SCIENCE = "Regulatory Science"
    REAL_WORLD_DATA = "Real World Data/Evidence"
    BIOINFORMATICS = "Bioinformatics"
    MEDICAL_IMAGING = "Medical Imaging AI"
    NLP_HEALTHCARE = "NLP in Healthcare"
    OTHER = "Other"


class ContactStatus(str, Enum):
    """Contact status options."""
    NOT_CONTACTED = "Not Contacted"
    CONTACTED = "Contacted"
    IN_DISCUSSION = "In Discussion"
    CONFIRMED = "Confirmed"
    DECLINED = "Declined"
    MAYBE_LATER = "Maybe Later"
    NO_RESPONSE = "No Response"


class Priority(str, Enum):
    """Priority levels."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class SpeakerBase(BaseModel):
    """Base speaker model with common fields."""
    name: str = Field(..., description="Speaker's full name")
    field_specialty: Optional[FieldSpecialty] = Field(None, description="Primary field/specialty")
    affiliation: Optional[str] = Field(None, description="University or company")
    position: Optional[str] = Field(None, description="Job title")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    potential_topics: Optional[list[str]] = Field(default_factory=list, description="Topics they could speak on")
    contact_status: ContactStatus = Field(default=ContactStatus.NOT_CONTACTED, description="Current contact status")
    research_notes: Optional[str] = Field(None, description="Bio summary and research findings")
    email: Optional[str] = Field(None, description="Contact email address")
    priority: Optional[Priority] = Field(None, description="Priority level for outreach")


class SpeakerCreate(SpeakerBase):
    """Model for creating a new speaker."""
    pass


class SpeakerUpdate(BaseModel):
    """Model for updating a speaker (all fields optional)."""
    name: Optional[str] = Field(None, description="Speaker's full name")
    field_specialty: Optional[FieldSpecialty] = Field(None, description="Primary field/specialty")
    affiliation: Optional[str] = Field(None, description="University or company")
    position: Optional[str] = Field(None, description="Job title")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    potential_topics: Optional[list[str]] = Field(None, description="Topics they could speak on")
    contact_status: Optional[ContactStatus] = Field(None, description="Current contact status")
    research_notes: Optional[str] = Field(None, description="Bio summary and research findings")
    email: Optional[str] = Field(None, description="Contact email address")
    priority: Optional[Priority] = Field(None, description="Priority level for outreach")


class Speaker(SpeakerBase):
    """Full speaker model with Notion metadata."""
    id: str = Field(..., description="Notion page ID")
    url: Optional[str] = Field(None, description="Notion page URL")

    class Config:
        from_attributes = True
