import os
from unittest import TestCase

from jira.exceptions import JIRAError
from mock import MagicMock, patch

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

    def test_create_jira_issues(self):
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

        output = self.handler.create_jira_issues([ticket], project)

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

    def test_create_jira_issue_cannot_craete(self):
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
