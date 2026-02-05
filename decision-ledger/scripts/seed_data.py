#!/usr/bin/env python3
"""
Seed data script for Decision Ledger DynamoDB table.

This script populates the DynamoDB table with sample data for local development.

Usage:
    # For DynamoDB Local
    python seed_data.py --endpoint http://localhost:8000

    # For AWS DynamoDB (requires credentials)
    python seed_data.py --table decision-ledger-dev
"""

import argparse
import uuid
from datetime import datetime, timedelta
from typing import Optional

import boto3
from botocore.config import Config


def get_dynamodb_client(endpoint_url: Optional[str] = None, region: str = "us-east-1"):
    """Get DynamoDB client, optionally pointing to local endpoint."""
    config = Config(retries={"max_attempts": 3, "mode": "standard"})

    if endpoint_url:
        return boto3.client(
            "dynamodb",
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id="local",
            aws_secret_access_key="local",
            config=config,
        )
    return boto3.client("dynamodb", region_name=region, config=config)


def generate_uuid() -> str:
    """Generate a new UUID."""
    return str(uuid.uuid4())


def iso_now() -> str:
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat() + "Z"


def iso_past(days: int) -> str:
    """Get timestamp N days ago in ISO format."""
    return (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"


def seed_data(client, table_name: str):
    """Seed the table with sample data."""

    print(f"Seeding table: {table_name}")

    # ==========================================================================
    # Sample Projects
    # ==========================================================================

    project1_id = generate_uuid()
    project2_id = generate_uuid()

    projects = [
        {
            "PK": {"S": f"PROJECT#{project1_id}"},
            "SK": {"S": "METADATA"},
            "entity_type": {"S": "PROJECT"},
            "id": {"S": project1_id},
            "name": {"S": "Backend Rewrite"},
            "description": {"S": "Modernizing the backend infrastructure"},
            "slack_channels": {"L": [{"S": "#backend"}, {"S": "#engineering"}]},
            "auto_confirm_meeting_decisions": {"BOOL": False},
            "notification_channel": {"S": "#backend-decisions"},
            "created_at": {"S": iso_past(30)},
            "updated_at": {"S": iso_past(30)},
        },
        {
            "PK": {"S": f"PROJECT#{project2_id}"},
            "SK": {"S": "METADATA"},
            "entity_type": {"S": "PROJECT"},
            "id": {"S": project2_id},
            "name": {"S": "Mobile App v2"},
            "description": {"S": "Next generation mobile application"},
            "slack_channels": {"L": [{"S": "#mobile"}, {"S": "#product"}]},
            "auto_confirm_meeting_decisions": {"BOOL": True},
            "notification_channel": {"S": "#mobile-updates"},
            "created_at": {"S": iso_past(60)},
            "updated_at": {"S": iso_past(15)},
        },
    ]

    for project in projects:
        client.put_item(TableName=table_name, Item=project)
        print(f"  Created project: {project['name']['S']}")

    # ==========================================================================
    # Sample Project Members
    # ==========================================================================

    members = [
        # Project 1 members
        {
            "PK": {"S": f"PROJECT#{project1_id}"},
            "SK": {"S": "MEMBER#U001"},
            "entity_type": {"S": "PROJECT_MEMBER"},
            "user_id": {"S": "U001"},
            "project_id": {"S": project1_id},
            "role": {"S": "admin"},
            "created_at": {"S": iso_past(30)},
        },
        {
            "PK": {"S": f"PROJECT#{project1_id}"},
            "SK": {"S": "MEMBER#U002"},
            "entity_type": {"S": "PROJECT_MEMBER"},
            "user_id": {"S": "U002"},
            "project_id": {"S": project1_id},
            "role": {"S": "member"},
            "created_at": {"S": iso_past(25)},
        },
        # Project 2 members
        {
            "PK": {"S": f"PROJECT#{project2_id}"},
            "SK": {"S": "MEMBER#U001"},
            "entity_type": {"S": "PROJECT_MEMBER"},
            "user_id": {"S": "U001"},
            "project_id": {"S": project2_id},
            "role": {"S": "member"},
            "created_at": {"S": iso_past(60)},
        },
        {
            "PK": {"S": f"PROJECT#{project2_id}"},
            "SK": {"S": "MEMBER#U003"},
            "entity_type": {"S": "PROJECT_MEMBER"},
            "user_id": {"S": "U003"},
            "project_id": {"S": project2_id},
            "role": {"S": "admin"},
            "created_at": {"S": iso_past(60)},
        },
    ]

    for member in members:
        client.put_item(TableName=table_name, Item=member)
    print(f"  Created {len(members)} project members")

    # ==========================================================================
    # Sample Decisions
    # ==========================================================================

    decision1_id = generate_uuid()
    decision2_id = generate_uuid()
    decision3_id = generate_uuid()
    decision4_id = generate_uuid()  # This one supersedes decision1

    decisions = [
        # Decision 1: Original decision (will be superseded)
        {
            "PK": {"S": f"DECISION#{decision1_id}"},
            "SK": {"S": "METADATA"},
            "entity_type": {"S": "DECISION"},
            "id": {"S": decision1_id},
            "project_id": {"S": project1_id},
            "summary": {"S": "Launch date set for March 15th"},
            "context": {"S": "Based on current progress and team capacity, we agreed on March 15th as the target launch date."},
            "raw_content": {"S": "Team discussed timeline. Everyone agreed March 15th works. @DecisionLedger"},
            "status": {"S": "superseded"},
            "source_type": {"S": "slack"},
            "source_channel": {"S": "#backend"},
            "source_url": {"S": "https://slack.com/archives/C001/p1234567890"},
            "source_timestamp": {"S": iso_past(20)},
            "author": {"S": "U001"},
            "participants": {"L": [
                {"M": {"name": {"S": "Alice"}, "role": {"S": "decider"}}},
                {"M": {"name": {"S": "Bob"}, "role": {"S": "approver"}}},
            ]},
            "tags": {"L": [{"S": "timeline"}, {"S": "launch"}]},
            "created_at": {"S": iso_past(20)},
            "updated_at": {"S": iso_past(20)},
            "gsi3_pk": {"S": f"superseded#{project1_id}"},
        },
        # Decision 2: Confirmed decision
        {
            "PK": {"S": f"DECISION#{decision2_id}"},
            "SK": {"S": "METADATA"},
            "entity_type": {"S": "DECISION"},
            "id": {"S": decision2_id},
            "project_id": {"S": project1_id},
            "summary": {"S": "Use DynamoDB for the new service"},
            "context": {"S": "After evaluating PostgreSQL and DynamoDB, we chose DynamoDB for its serverless nature and scalability."},
            "raw_content": {"S": "We're going with DynamoDB for the new service @DecisionLedger"},
            "status": {"S": "confirmed"},
            "source_type": {"S": "slack"},
            "source_channel": {"S": "#backend"},
            "source_url": {"S": "https://slack.com/archives/C001/p1234567891"},
            "source_timestamp": {"S": iso_past(15)},
            "author": {"S": "U002"},
            "participants": {"L": [
                {"M": {"name": {"S": "Bob"}, "role": {"S": "decider"}}},
                {"M": {"name": {"S": "Charlie"}, "role": {"S": "contributor"}}},
            ]},
            "tags": {"L": [{"S": "database"}, {"S": "infrastructure"}]},
            "created_at": {"S": iso_past(15)},
            "updated_at": {"S": iso_past(15)},
            "gsi3_pk": {"S": f"confirmed#{project1_id}"},
        },
        # Decision 3: Open decision (still discussing)
        {
            "PK": {"S": f"DECISION#{decision3_id}"},
            "SK": {"S": "METADATA"},
            "entity_type": {"S": "DECISION"},
            "id": {"S": decision3_id},
            "project_id": {"S": project2_id},
            "summary": {"S": "Evaluating React Native vs Flutter for mobile app"},
            "context": {"S": "Team is researching both options. Will decide after POC phase."},
            "raw_content": {"S": "We need to decide between React Native and Flutter @DecisionLedger"},
            "status": {"S": "open"},
            "source_type": {"S": "meeting"},
            "source_channel": {"S": "Weekly Standup"},
            "source_timestamp": {"S": iso_past(5)},
            "author": {"S": "U003"},
            "participants": {"L": [
                {"M": {"name": {"S": "Charlie"}, "role": {"S": "contributor"}}},
                {"M": {"name": {"S": "Diana"}, "role": {"S": "contributor"}}},
            ]},
            "tags": {"L": [{"S": "mobile"}, {"S": "framework"}, {"S": "tech-stack"}]},
            "created_at": {"S": iso_past(5)},
            "updated_at": {"S": iso_past(5)},
            "gsi3_pk": {"S": f"open#{project2_id}"},
        },
        # Decision 4: Supersedes decision 1
        {
            "PK": {"S": f"DECISION#{decision4_id}"},
            "SK": {"S": "METADATA"},
            "entity_type": {"S": "DECISION"},
            "id": {"S": decision4_id},
            "project_id": {"S": project1_id},
            "summary": {"S": "Launch date moved to April 1st"},
            "context": {"S": "Due to additional requirements, we're pushing the launch to April 1st."},
            "raw_content": {"S": "Launch date moved to April 1st due to new requirements @DecisionLedger"},
            "status": {"S": "confirmed"},
            "supersedes_id": {"S": decision1_id},
            "source_type": {"S": "slack"},
            "source_channel": {"S": "#backend"},
            "source_url": {"S": "https://slack.com/archives/C001/p1234567892"},
            "source_timestamp": {"S": iso_past(3)},
            "author": {"S": "U001"},
            "participants": {"L": [
                {"M": {"name": {"S": "Alice"}, "role": {"S": "decider"}}},
                {"M": {"name": {"S": "Bob"}, "role": {"S": "approver"}}},
            ]},
            "tags": {"L": [{"S": "timeline"}, {"S": "launch"}]},
            "created_at": {"S": iso_past(3)},
            "updated_at": {"S": iso_past(3)},
            "gsi3_pk": {"S": f"confirmed#{project1_id}"},
        },
    ]

    for decision in decisions:
        client.put_item(TableName=table_name, Item=decision)
        print(f"  Created decision: {decision['summary']['S'][:50]}...")

    print(f"\nSeed data complete!")
    print(f"  Projects: {len(projects)}")
    print(f"  Members: {len(members)}")
    print(f"  Decisions: {len(decisions)}")


def main():
    parser = argparse.ArgumentParser(description="Seed Decision Ledger DynamoDB table")
    parser.add_argument(
        "--endpoint",
        default="http://localhost:8000",
        help="DynamoDB endpoint URL (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--table",
        default="decision-ledger",
        help="DynamoDB table name (default: decision-ledger)",
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS region (default: us-east-1)",
    )

    args = parser.parse_args()

    client = get_dynamodb_client(endpoint_url=args.endpoint, region=args.region)
    seed_data(client, args.table)


if __name__ == "__main__":
    main()
