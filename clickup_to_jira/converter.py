import os
from logging import getLogger

from clickup_to_jira.ticket import Ticket

logger = getLogger(__name__)


class ClickUpToJIRAConverter:
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

        :param Ticket tickets: The tickets to be converted
        :return: The converted tickets
        :rtype: list(Ticket)
        """
        converted_tickets = list()
        for ticket in tickets:
            converted_tickets.append(self.convert_ticket(ticket))
        return converted_tickets

    def convert_ticket(self, ticket):
        logger.info(f"converting ticket {ticket.name}")
        ticket_type = ",".join([tag.name for tag in ticket.tags])
        ticket_description = self.get_converted_description(ticket.description)
        ticket_status = ticket.status.status
        subtasks = self.get_converted_subtasks(ticket.linked_tasks)
        if ticket.assignees:
            ticket_assignee = ticket.assignees[0]
        else:
            ticket_assignee = None
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

    def get_converted_description(self, description):
        return description

    def get_converted_subtasks(self, subtasks):
        return [self.convert_ticket(subtask) for subtask in subtasks]
