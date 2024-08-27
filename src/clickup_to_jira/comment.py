from dataclasses import dataclass


@dataclass
class Comment:
    """
    Class responsible for hosting comments of all JIRA and Clickup
    """

    id: str
    text: str
    commenter: str
