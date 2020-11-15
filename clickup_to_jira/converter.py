import os
from logging import getLogger

from clickup_to_jira.ticket import Ticket

logger = getLogger(__name__)


class ClickUpToJIRAConverter:
    """
    Class responsible for converting ClickUp Tickets to JIRA Tickets.
    """

    def __init__(self, click_up_handler, jira_handler):
        """
        Initialize the converter.

        :param ClickUpHandler click_up_handler: The ClickUp handler
        :param JIRAHandler jira_handler: The JIRA handler
        """
        self.click_up = click_up_handler
        self.jira = jira_handler

    def convert(self, tickets):
        """
        Convert ClickUp tickets to JIRA tickets.

        :param list(Ticket) tickets: The tickets to be converted
        :return: The converted tickets
        :rtype: list(Ticket)
        """
        converted_tickets = list()
        for ticket in tickets:
            converted_tickets.append(self.convert_ticket(ticket))
        return converted_tickets

    def convert_ticket(self, ticket):
        """
        Covert ClickUp ticket to DataClass Ticket.

        :param ClickUp.Ticket ticket: The incoming Ticker
        :return: The dataclass Ticket
        :rtype: Ticket
        """
        logger.info(f"converting ticket {ticket.name}")

        # Prepare entities for ticket
        ticket_type = ",".join([tag.name for tag in ticket.tags])
        ticket_description = self._get_converted_description(
            ticket.description
        )
        ticket_status = ticket.status.status
        subtasks = self._get_converted_subtasks(ticket.linked_tasks)

        # Handle assignees
        if ticket.assignees:
            ticket_assignee = ticket.assignees[0]
        else:
            ticket_assignee = None

        # Return the new Ticket
        return Ticket(
            id=ticket.id,
            type=ticket_type,
            project=os.getenv("JIRA_PROJECT"),
            title=ticket.name,
            description=ticket_description,
            subtasks=subtasks,
            status=ticket_status,
            assignee=ticket_assignee,
            comments=ticket.comments,
            parent=ticket.parent,
        )

    @staticmethod
    def _get_converted_description(description):
        """
        Get the converted description.

        :param str description: The incoming description
        :return: The edited description
        :rtype: str
        """
        # todo Transform ClickUp Markdown to JIRA Markdown
        return description

    def _get_converted_subtasks(self, subtasks):
        """
        Get Converted subtasks.

        :param list(ClickUp.Ticket) subtasks: The ClickUp sub tickets
        :return: The edited sub tickets
        :rtype: list(Ticket)
        """
        return [self.convert_ticket(subtask) for subtask in subtasks]
