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
        ticket_type = self.get_converted_type(
            [tag.name for tag in ticket.tags]
        )
        ticket_description = self.get_converted_description(ticket.description)
        ticket_status = self.get_converted_status(ticket.status.status)
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

    def get_converted_type(self, clickup_labels):
        type_mappings = {
            "bug": "Bug",
            "backend": "Task",
            "node": "Task",
            "proposed_from_tech_leader": "Task",
            "spike": "Task",
            "task": "Task",
            "frontend": "Task",
            "devops": "Task",
            "django": "Task",
            "ci/cd": "Task",
            "data": "Task",
            "documentation": "Task",
            "enhancement": "Story",
            # "epic": "Epic",
        }
        for clickup_label in clickup_labels:
            try:
                return type_mappings[clickup_label]
            except KeyError:
                continue
        return "Story"

    def get_converted_description(self, description):
        return description

    def get_converted_subtasks(self, subtasks):
        return [self.convert_ticket(subtask) for subtask in subtasks]

    def get_converted_status(self, status):
        status_mappings = {
            "backlog p1": "READY FOR DEVELOPMENT",
            "backlog p2": "Backlog",
            "backlog p3": "Analysis",
            "bugs": "READY FOR DEVELOPMENT",
            "development-done": "Dev Done",
            "development-in progress": "In Progress",
            "on hold": "ON HOLD",
            "finished": "Done",
            "qa-in progress": "QA",
            "Open": "READY FOR DEVELOPMENT",
            "to do": "To Do",
            "dev done": "Dev Done",
            "in progress": "In Progress",
            "in review": "In Review",
            "Closed": "Done",
            "deployed": "Done",
            "ready to deploy": "Done",
            "qa": "QA",
            "has issues": "Has Issues",
            "ideas": "Ideas",
        }
        try:
            return status_mappings[status]
        except KeyError:
            return "Open"
