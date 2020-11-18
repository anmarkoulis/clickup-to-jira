import os

from clickup_to_jira.converter import ClickUpToJIRAConverter
from clickup_to_jira.handlers import ClickUpHandler, JIRAHandler
from clickup_to_jira.utils import initialize_logging


def main():
    """
    Create JIRA issues from ClickUp tasks.
    """
    # Initialize logging
    initialize_logging()

    # Initialize handlers
    click_up_handler = ClickUpHandler(os.getenv("CLICKUP_API_KEY"))
    jira_handler = JIRAHandler(
        os.getenv("JIRA_URL"),
        basic_auth=(os.getenv("JIRA_USER"), os.getenv("JIRA_API_KEY")),
    )

    # Setup Converter
    converter = ClickUpToJIRAConverter(click_up_handler, jira_handler)

    # Get tickets from ClickUp
    tickets = click_up_handler.get_click_up_tickets()

    # Convert them to JIRA tickets
    new_tickets = converter.convert(tickets)

    # Create JIRA tickets
    jira_handler.create_jira_issues(new_tickets)


if __name__ == "__main__":  # pragma: no cover
    main()
