from dataclasses import dataclass


@dataclass
class Ticket:
    """
    Class responsible for hosting tickets of all JIRA and ClickUp
    """

    id: str
    type: str
    project: str
    title: str
    description: str
    subtasks: list
    status: str
    creator: str
    assignee: str
    parent: str
    comments: list
    url: str
