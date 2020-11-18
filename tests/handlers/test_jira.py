import json
import os
from unittest import TestCase

from jira.exceptions import JIRAError
from jira.resources import User
from mock import MagicMock, call, patch

from clickup_to_jira.handlers.jira import JIRAHandler


class TestJIRAHandler(TestCase):
    @patch.dict(
        os.environ,
        {
            "JIRA_URL": "https://jira_url",
            "JIRA_USER": "user",
            "JIRA_API_KEY": "key",  # pragma: allowlist secret
        },
    )  # pylint: disable=arguments-differ
    @patch("clickup_to_jira.handlers.jira.JIRAHandler.__init__")
    def setUp(self, handler__init):
        handler__init.return_value = None
        self.handler = JIRAHandler(
            os.getenv("JIRA_URL"),
            basic_auth=(os.getenv("JIRA_USER"), os.getenv("JIRA_API_KEY")),
        )

    @patch("clickup_to_jira.handlers.jira.get_item_from_user_input")
    def test_create_jira_issues(self, get_item):
        self.handler.projects = MagicMock()
        self.handler.create_type_mappings = MagicMock()
        self.handler.create_jira_issue = MagicMock()

        project = "project"
        ticket = MagicMock()
        jira_project = MagicMock()
        jira_project.id = 1
        jira_project.name = project

        jira_issue = MagicMock()

        self.handler.projects.return_value = [jira_project]
        self.handler.create_jira_issue.side_effect = [jira_issue]
        get_item.return_value = jira_project

        output = self.handler.create_jira_issues([ticket])

        self.assertEqual(output, [jira_issue])
        self.handler.create_jira_issue.assert_called_once_with(
            ticket, jira_project.id
        )

    def test_create_jira_issue_sunny_day(self):
        self.handler.get_issue_from_summary = MagicMock()
        self.handler.create_base_jira_issue = MagicMock()
        self.handler.assign_issue_to_user = MagicMock()
        self.handler.transition_issue_to_proper_status = MagicMock()
        self.handler.add_comments = MagicMock()

        project = "project"
        ticket = MagicMock()
        title = "title"
        ticket.title = title

        jira_issue = MagicMock()

        self.handler.get_issue_from_summary.return_value = False
        self.handler.create_base_jira_issue.return_value = jira_issue

        self.handler.create_jira_issue(ticket, project)

        self.handler.get_issue_from_summary.assert_called_once_with(
            project,
            ticket.title,
        )
        self.handler.create_base_jira_issue.assert_called_once_with(
            ticket, project
        )
        self.handler.assign_issue_to_user.assert_called_once_with(
            jira_issue,
            ticket,
        )
        self.handler.transition_issue_to_proper_status.assert_called_once_with(
            jira_issue,
            ticket,
        )
        self.handler.add_comments.assert_called_once_with(
            jira_issue,
            ticket,
        )

    def test_create_jira_issue_already_exists(self):
        self.handler.get_issue_from_summary = MagicMock()
        self.handler.create_base_jira_issue = MagicMock()
        self.handler.assign_issue_to_user = MagicMock()
        self.handler.transition_issue_to_proper_status = MagicMock()
        self.handler.add_comments = MagicMock()

        project = "project"
        ticket = MagicMock()
        title = "title"
        ticket.title = title

        jira_issue = MagicMock()

        self.handler.get_issue_from_summary.return_value = True
        self.handler.create_base_jira_issue.return_value = jira_issue

        self.handler.create_jira_issue(ticket, project)

        self.handler.get_issue_from_summary.assert_called_once_with(
            project,
            ticket.title,
        )
        self.handler.create_base_jira_issue.assert_not_called()
        self.handler.assign_issue_to_user.assert_not_called()
        self.handler.transition_issue_to_proper_status.assert_not_called()
        self.handler.add_comments.assert_not_called()

    def test_create_jira_issue_cannot_get_existing(self):
        self.handler.get_issue_from_summary = MagicMock()
        self.handler.create_base_jira_issue = MagicMock()
        self.handler.assign_issue_to_user = MagicMock()
        self.handler.transition_issue_to_proper_status = MagicMock()
        self.handler.add_comments = MagicMock()

        project = "project"
        ticket = MagicMock()
        title = "title"
        ticket.title = title

        jira_issue = MagicMock()

        self.handler.get_issue_from_summary.side_effect = JIRAError("Error")
        self.handler.create_base_jira_issue.return_value = jira_issue

        self.handler.create_jira_issue(ticket, project)

        self.handler.get_issue_from_summary.assert_called_once_with(
            project,
            ticket.title,
        )
        self.handler.create_base_jira_issue.assert_not_called()
        self.handler.assign_issue_to_user.assert_not_called()
        self.handler.transition_issue_to_proper_status.assert_not_called()
        self.handler.add_comments.assert_not_called()

    def test_create_jira_issue_cannot_create(self):
        self.handler.get_issue_from_summary = MagicMock()
        self.handler.create_base_jira_issue = MagicMock()
        self.handler.assign_issue_to_user = MagicMock()
        self.handler.transition_issue_to_proper_status = MagicMock()
        self.handler.add_comments = MagicMock()

        project = "project"
        ticket = MagicMock()
        title = "title"
        ticket.title = title

        jira_issue = None

        self.handler.get_issue_from_summary.return_value = False
        self.handler.create_base_jira_issue.return_value = jira_issue

        self.handler.create_jira_issue(ticket, project)

        self.handler.get_issue_from_summary.assert_called_once_with(
            project,
            ticket.title,
        )
        self.handler.create_base_jira_issue.assert_called_once_with(
            ticket, project
        )
        self.handler.assign_issue_to_user.assert_not_called()
        self.handler.transition_issue_to_proper_status.assert_not_called()
        self.handler.add_comments.assert_not_called()

    def test_create_vase_jira_issue_sunny_day(self):
        self.handler.get_issue_from_summary = MagicMock()
        self.handler.create_issue = MagicMock()

        project = "project"
        ticket = MagicMock()
        title = "title"
        ticket.title = title

        jira_issue = MagicMock()

        self.handler.get_issue_from_summary.return_value = jira_issue
        self.handler.create_issue.return_value = jira_issue
        output = self.handler.create_base_jira_issue(ticket, project)
        self.assertEqual(output, jira_issue)

    def test_create_vase_jira_issue_creation_error(self):
        self.handler.get_issue_from_summary = MagicMock()
        self.handler.create_issue = MagicMock()

        project = "project"
        ticket = MagicMock()
        title = "title"
        ticket.title = title

        jira_issue = MagicMock()

        self.handler.get_issue_from_summary.return_value = jira_issue
        self.handler.create_issue.side_effect = JIRAError()
        output = self.handler.create_base_jira_issue(ticket, project)
        self.assertEqual(output, None)

    def test_assign_issue_to_user(self):
        self.handler.search_users = MagicMock()
        self.handler.assign_issue = MagicMock()

        user = MagicMock()
        user_account_id = MagicMock()
        user_account_id.accountId = user
        self.handler.search_users.return_value = [user_account_id]

        ticket = MagicMock()
        assignee = "assignee"
        ticket.assignee = assignee
        jira_issue = MagicMock()

        self.handler.assign_issue_to_user(jira_issue, ticket)

        self.handler.search_users.assert_called_once_with(user=assignee)
        self.handler.assign_issue.assert_called_once_with(jira_issue, user)

    def test_assign_issue_to_user_error(self):
        self.handler.search_users = MagicMock()
        self.handler.assign_issue = MagicMock()

        user = MagicMock()
        user_account_id = MagicMock()
        user_account_id.accountId = user
        self.handler.search_users.return_value = [user_account_id]
        self.handler.assign_issue.side_effect = JIRAError()

        ticket = MagicMock()
        assignee = "assignee"
        ticket.assignee = assignee
        jira_issue = MagicMock()

        self.handler.assign_issue_to_user(jira_issue, ticket)

        self.handler.search_users.assert_called_once_with(user=assignee)
        self.handler.assign_issue.assert_called_once_with(jira_issue, user)

    def test_transition_issue_to_proper_status(self):
        self.handler.update_status_mappings = MagicMock()
        self.handler.transition_issue = MagicMock()

        ticket = MagicMock()
        status = "status"
        ticket.status = status
        jira_issue = MagicMock()

        self.handler.status_mappings[status] = status

        self.handler.transition_issue_to_proper_status(jira_issue, ticket)

        self.handler.update_status_mappings.assert_not_called()
        self.handler.transition_issue.assert_called_once_with(
            jira_issue, status
        )

    def test_transition_issue_to_proper_status_transition_error(self):
        self.handler.update_status_mappings = MagicMock()
        self.handler.transition_issue = MagicMock()

        ticket = MagicMock()
        status = "status"
        ticket.status = status
        jira_issue = MagicMock()

        self.handler.status_mappings[status] = status
        self.handler.transition_issue.side_effect = JIRAError()
        self.handler.transition_issue_to_proper_status(jira_issue, ticket)

        self.handler.update_status_mappings.assert_not_called()
        self.handler.transition_issue.assert_called_once_with(
            jira_issue, status
        )

    def test_transition_issue_to_proper_status_mapping_error(self):
        self.handler.update_status_mappings = MagicMock()
        self.handler.transition_issue = MagicMock()

        ticket = MagicMock()
        status = "status"
        ticket.status = status
        jira_issue = MagicMock()

        self.handler.status_mappings = {}
        self.handler.update_status_mappings.side_effect = JIRAError()

        self.handler.transition_issue_to_proper_status(jira_issue, ticket)

        self.handler.update_status_mappings.assert_called_once()
        self.handler.transition_issue.assert_not_called()

    @patch("builtins.input")
    def test_update_status_mappings_not_exists_in_mappings(self, input_mock):
        self.handler.transitions = MagicMock()

        ticket = MagicMock()
        status = "status"
        ticket.status = status
        jira_issue = MagicMock()
        jira_status = "To Do"
        transition = {"to": {"name": jira_status}}

        input_mock.side_effect = ["Error", jira_status]
        self.handler.transitions.return_value = [transition]
        self.handler.status_mappings = {}

        self.handler.update_status_mappings(ticket, jira_issue)

        self.assertEqual(input_mock.call_count, 2)

    @patch("builtins.input")
    def test_update_status_mappings_already_exists_in_mappings(
        self, input_mock
    ):
        self.handler.transitions = MagicMock()

        ticket = MagicMock()
        status = "status"
        ticket.status = status
        jira_issue = MagicMock()
        jira_status = "To Do"
        transition = {"to": {"name": jira_status}}

        input_mock.side_effect = [jira_status]
        self.handler.transitions.return_value = [transition]
        self.status_mappings = {status: jira_status}

        self.handler.update_status_mappings(ticket, jira_issue)

        self.assertEqual(input_mock.call_count, 0)

    @patch("builtins.input")
    def test_update_status_mappings_mapping_set_properly_at_once(
        self, input_mock
    ):
        self.handler.transitions = MagicMock()

        ticket = MagicMock()
        status = "status"
        ticket.status = status
        jira_issue = MagicMock()
        jira_status = "To Do"
        transition = {"to": {"name": jira_status}}

        input_mock.side_effect = [jira_status]
        self.handler.transitions.return_value = [transition]
        self.handler.status_mappings = {}

        self.handler.update_status_mappings(ticket, jira_issue)

        self.assertEqual(input_mock.call_count, 1)

    @patch("builtins.input")
    def test_create_type_mappings_use_default_mappings_with_story(
        self, input_mock
    ):
        self.handler.issue_types = MagicMock()

        ticket = MagicMock()
        ticket_type = "bug,ci"
        ticket.type = ticket_type
        issue_type = MagicMock()
        issue_type.name = "Story"
        issue_types = [issue_type]

        self.handler.issue_types.return_value = issue_types

        input_mock.side_effect = ["Y"]

        mappings = self.handler.create_type_mappings([ticket])

        self.assertEqual(mappings, {"bug": "Story", "ci": "Story"})
        self.assertEqual(input_mock.call_count, 1)

    @patch("builtins.input")
    def test_create_type_mappings_use_default_mappings_no_story(
        self, input_mock
    ):
        self.handler.issue_types = MagicMock()

        ticket = MagicMock()
        ticket_type = "bug,ci"
        ticket.type = ticket_type
        issue_type = MagicMock()
        issue_type.name = "Bug"
        issue_types = [issue_type]

        self.handler.issue_types.return_value = issue_types

        input_mock.side_effect = ["Y"]

        mappings = self.handler.create_type_mappings([ticket])

        self.assertEqual(mappings, {"bug": "Bug", "ci": "Bug"})
        self.assertEqual(input_mock.call_count, 1)

    @patch("builtins.input")
    def test_create_type_mappings_use_custom_mappings(self, input_mock):
        self.handler.issue_types = MagicMock()

        ticket = MagicMock()
        ticket_type = "bug,ci"
        ticket.type = ticket_type
        issue_type = MagicMock()
        issue_type.name = "Story"
        issue_types = [issue_type]

        self.handler.issue_types.return_value = issue_types

        input_mock.side_effect = ["N", "Error", "Story", "Story"]

        mappings = self.handler.create_type_mappings([ticket])

        self.assertEqual(mappings, {"bug": "Story", "ci": "Story"})
        self.assertEqual(input_mock.call_count, 4)

    @patch("builtins.input")
    def test_create_type_mappings_first_error_then_default(self, input_mock):
        self.handler.issue_types = MagicMock()

        ticket = MagicMock()
        ticket_type = "bug,ci"
        ticket.type = ticket_type
        issue_type = MagicMock()
        issue_type.name = "Story"
        issue_types = [issue_type]

        self.handler.issue_types.return_value = issue_types

        input_mock.side_effect = ["Error", "Y"]

        mappings = self.handler.create_type_mappings([ticket])

        self.assertEqual(mappings, {"bug": "Story", "ci": "Story"})
        self.assertEqual(input_mock.call_count, 2)

    @patch("builtins.input")
    def test_create_type_mappings_first_error_then_custom(self, input_mock):
        self.handler.issue_types = MagicMock()

        ticket = MagicMock()
        ticket_type = "bug,ci"
        ticket.type = ticket_type
        issue_type = MagicMock()
        issue_type.name = "Story"
        issue_types = [issue_type]

        self.handler.issue_types.return_value = issue_types

        input_mock.side_effect = ["Error", "N", "Story", "Story"]

        mappings = self.handler.create_type_mappings([ticket])

        self.assertEqual(mappings, {"bug": "Story", "ci": "Story"})
        self.assertEqual(input_mock.call_count, 4)

    def test_add_comments(self):
        self.handler.add_comment = MagicMock()

        comment_1 = MagicMock()
        comment_1.commenter = "commenter@mail.com"
        comment_1.text = "Do that"

        comment_2 = MagicMock()
        comment_2.commenter = "commenter2@mail.com"
        comment_2.text = "Did it"

        comments = [comment_1, comment_2]

        ticket = MagicMock()
        ticket.comments = comments
        jira_issue = MagicMock()
        self.handler.add_comment.side_effect = [None, JIRAError]

        self.handler.add_comments(jira_issue, ticket)

        self.handler.add_comment.assert_has_calls(
            calls=[
                call(
                    jira_issue, f"{comment_1.commenter} said: {comment_1.text}"
                ),
                call(
                    jira_issue, f"{comment_2.commenter} said: {comment_2.text}"
                ),
            ]
        )

    def test_get_issue_from_summary(self):
        self.handler.search_issues = MagicMock()

        issue_1 = MagicMock()
        issue_1.fields.summary = "This is a story"
        issue_2 = MagicMock()
        issue_2.fields.summary = "This is a story I want to pick"

        self.handler.search_issues.return_value = [issue_1, issue_2]

        summary = "This is a story I want to pick"
        output = self.handler.get_issue_from_summary("project", summary)
        self.assertEqual(output, [issue_2])

    def test_search_users(self):
        self.handler._fetch_pages = MagicMock()
        response = MagicMock()
        user = MagicMock()

        self.handler._fetch_pages.return_value = response
        output = self.handler.search_users(user)

        self.handler._fetch_pages.assert_called_once_with(
            User,
            None,
            "user/search",
            0,
            50,
            {
                "query": user,
                "includeActive": True,
                "includeInactive": False,
            },
        )
        self.assertEqual(output, response)

    def test_assign_issue(self):
        session = MagicMock()

        self.handler._session = session
        self.handler._options = {"server": "server"}
        jira_issue = "issue"
        assignee = "assignee"

        output = self.handler.assign_issue(jira_issue, assignee)

        self.assertEqual(output, True)
        session.put.assert_called_once_with(
            "server/rest/api/latest/issue/issue/assignee",
            data=json.dumps({"accountId": assignee}),
        )
