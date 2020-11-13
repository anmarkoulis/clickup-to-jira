import os

from clickup_to_jira.converter import ClickUpToJIRAConverter
from clickup_to_jira.handlers import ClickUpHandler, JIRAHandler
from clickup_to_jira.utils import get_cli_arguments, initialize_logging


def main():
    """
    Create JIRA issues from ClickUp tasks.
    """
    # Initialize logging
    initialize_logging()

    # Get cli params
    cli_params = get_cli_arguments()

    # Initialize handlers
    click_up_handler = ClickUpHandler(os.getenv("CLICKUP_API_KEY"))
    jira_handler = JIRAHandler(
        os.getenv("JIRA_URL"),
        basic_auth=(os.getenv("JIRA_USER"), os.getenv("JIRA_API_KEY")),
    )

    # Setup Converter
    converter = ClickUpToJIRAConverter(click_up_handler, jira_handler)

    # Get tickets from ClickUp
    tickets = click_up_handler.get_click_up_tickets(
        cli_params.TEAM, cli_params.SPACE, cli_params.PROJECT, cli_params.LIST
    )

    # Convert them to JIRA tickets
    new_tickets = converter.convert(tickets)

    # Create JIRA tickets
    jira_handler.create_tickets(new_tickets, cli_params.JIRA_PROJECT)


if __name__ == "__main__":
    main()
