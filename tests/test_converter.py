from unittest import TestCase

from clickup_to_jira.converter import ClickUpToJIRAConverter
from mock import MagicMock, call


class TestClickUpToJIRAConverter(TestCase):
    def setUp(self) -> None:
        click_up_handler = MagicMock()
        jira_handler = MagicMock()
        self.converter = ClickUpToJIRAConverter(click_up_handler, jira_handler)

    def test_convert(self):
        click_up_handler = MagicMock()
        jira_handler = MagicMock()
        self.converter = ClickUpToJIRAConverter(click_up_handler, jira_handler)
        ticket_1 = MagicMock()
        ticket_2 = MagicMock()

        conv_ticket_1 = MagicMock()
        conv_ticket_2 = MagicMock()

        self.converter.convert_ticket = MagicMock()
        self.converter.convert_ticket.side_effect = [
            conv_ticket_1,
            conv_ticket_2,
        ]

        output = self.converter.convert([ticket_1, ticket_2])

        self.assertEqual(output, [conv_ticket_1, conv_ticket_2])
        self.converter.convert_ticket.assert_has_calls(
            calls=[call(ticket_1), call(ticket_2)]
        )

    def test_convert_ticket(self):
        name_sub = "Ticket Sub"
        tag_sub = MagicMock()
        tag_sub.name = "tag_sub"
        tags_sub = [tag_sub]
        description_sub = "Description Sbu"
        status_sub = "status sub"
        subtasks_sub = []
        assignees_sub = []
        id_sub = "1"
        parent_sub = "2"
        comments_sub = ["comment_1_sub"]

        sub_ticket = MagicMock()
        sub_ticket.id = id_sub
        sub_ticket.name = name_sub
        sub_ticket.tags = tags_sub
        sub_ticket.description = description_sub
        sub_ticket.status = MagicMock(status=status_sub)
        sub_ticket.linked_tasks = subtasks_sub
        sub_ticket.assignees = assignees_sub
        sub_ticket.parent = parent_sub
        sub_ticket.comments = comments_sub

        name = "Ticket"
        tag = MagicMock()
        tag.name = "tag"
        tags = [tag]
        description = "Description"
        status = "status"
        subtasks = [sub_ticket]
        assignees = ["assignee_1"]
        id_par = "2"
        parent = None
        comments = ["comment_1", "comment_2"]

        ticket = MagicMock()
        ticket.id = id_par
        ticket.name = name
        ticket.tags = tags
        ticket.description = description
        ticket.status = MagicMock(status=status)
        ticket.linked_tasks = subtasks
        ticket.assignees = assignees
        ticket.parent = parent
        ticket.comments = comments

        ticket.name = name

        output = self.converter.convert_ticket(ticket)

        self.assertEqual(output.id, id_par)
        self.assertEqual(output.title, name)
        self.assertEqual(output.project, None)
        self.assertEqual(output.description, description)
        self.assertEqual(output.status, status)
        self.assertEqual(output.title, name)
        self.assertEqual(output.assignee, assignees[0])
        self.assertEqual(output.comments, comments)
        self.assertEqual(output.parent, parent)

        self.assertEqual(output.subtasks[0].id, id_sub)
        self.assertEqual(output.subtasks[0].title, name_sub)
        self.assertEqual(output.subtasks[0].project, None)
        self.assertEqual(output.subtasks[0].description, description_sub)
        self.assertEqual(output.subtasks[0].status, status_sub)
        self.assertEqual(output.subtasks[0].title, name_sub)
        self.assertEqual(output.subtasks[0].assignee, None)
        self.assertEqual(output.subtasks[0].comments, comments_sub)
        self.assertEqual(output.subtasks[0].parent, parent_sub)
