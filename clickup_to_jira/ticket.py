from dataclasses import dataclass


@dataclass
class Ticket:
    """
    Class responsible for hosting tickets of all JIRA and Clickup
    """

    id: str
    type: str
    project: str
    title: str
    description: str
    subtasks: list
