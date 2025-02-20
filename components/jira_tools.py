from __future__ import annotations

import os

import jira


JIRA_EMAIL = "philipptemminghoff@gmail.com"
JIRA_TOKEN = os.getenv("JIRA_API_KEY")
SERVER = "https://philipptemminghoff.atlassian.net"


def create_issue(project: str, summary: str, description: str):
    """Create a new issue in Jira.

    Args:
        project: The project key.
        summary: The issue summary.
        description: The issue description.
        issuetype: The issue type.

    Returns:
        str: A message indicating the success of the operation.
    """
    assert JIRA_TOKEN
    jira_client = jira.JIRA(server=SERVER, basic_auth=(JIRA_EMAIL, JIRA_TOKEN))
    issue_type = {"name": "Bug"}
    issue = jira_client.create_issue(
        project=project,
        summary=summary,
        description=description,
        issuetype=issue_type,
    )
    return f"Issue {issue.id} created successfully"


if __name__ == "__main__":
    print(create_issue("SCRUM", "Test Issue", "This is a test issue"))
