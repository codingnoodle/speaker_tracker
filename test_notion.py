#!/usr/bin/env python3
"""Test script to verify Notion connection and database setup."""

import os
import sys

from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from sapa_speaker_tracker import NotionSpeakerClient


def main():
    """Test Notion connection."""
    # Load environment variables
    load_dotenv()

    api_key = os.getenv("NOTION_API_KEY")
    database_id = os.getenv("NOTION_DATABASE_ID")

    print("=" * 50)
    print("SAPA Speaker Tracker - Notion Connection Test")
    print("=" * 50)

    # Check environment variables
    if not api_key:
        print("\n[ERROR] NOTION_API_KEY not found in environment")
        print("Please create a .env file with your Notion integration token")
        print("See .env.example for the template")
        return False

    if not database_id:
        print("\n[ERROR] NOTION_DATABASE_ID not found in environment")
        print("Please add your database ID to the .env file")
        return False

    print(f"\nAPI Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"Database ID: {database_id}")

    # Test connection
    print("\nTesting connection...")
    try:
        client = NotionSpeakerClient(api_key=api_key, database_id=database_id)
        result = client.test_connection()

        if result["success"]:
            print(f"\n[SUCCESS] Connected to database!")
            print(f"Database Name: {result['database_title']}")
            print(f"Database ID: {result['database_id']}")

            # List existing speakers
            print("\n" + "-" * 50)
            print("Fetching existing speakers...")
            speakers = client.list_speakers(limit=5)
            if speakers:
                print(f"Found {len(speakers)} speaker(s):")
                for s in speakers:
                    print(f"  - {s.name} ({s.affiliation or 'No affiliation'})")
            else:
                print("No speakers in database yet (that's okay!)")

            print("\n" + "=" * 50)
            print("CONNECTION TEST PASSED!")
            print("=" * 50)
            return True

        else:
            print(f"\n[ERROR] Connection failed: {result['error']}")
            print("\nCommon issues:")
            print("1. Integration not connected to the database")
            print("   - Open your database in Notion")
            print("   - Click '...' -> 'Connections' -> Select your integration")
            print("2. Invalid API key or database ID")
            print("3. Integration lacks required permissions")
            return False

    except Exception as e:
        print(f"\n[ERROR] Exception: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
