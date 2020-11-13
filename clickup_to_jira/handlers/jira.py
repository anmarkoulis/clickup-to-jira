import json
from logging import getLogger

from jira import JIRA
from jira.exceptions import JIRAError
from jira.resources import User

logger = getLogger(__name__)


class JIRAHandler(JIRA):
    def create_ticket(self, ticket, project):
        """
        Create a JIRA ticket.

        :param Ticket ticket: The ticket to create
        :param str project: The project name
        :return: The new ticket
        :rtype: JIRA.issue
        """
        logger.info(f"Creating {ticket.title} in JIRA.")
        if self.get_issue_from_summary(project, ticket.title):
            logger.warning(f"Ticket {ticket.title} already exists.")
            return
        issue_data = {
            "project": project,
            "issuetype": {"name": ticket.type}
            if not ticket.parent
            else {"name": "Sub-task"},
            "summary": ticket.title,
            "description": ticket.description,
        }
        parent_list = self.get_issue_from_summary(project, ticket.parent)
        if parent_list:
            logger.info(f"Ticket {ticket.title} has parent")
            issue_data["parent"] = {"id": parent_list[0].id}

        try:
            issue = self.create_issue(**issue_data)
        except JIRAError:
            logger.exception("Cannot create issue. Move on")
            return
        logger.info(f"Create {issue}")
        try:
            user = self.search_users(user=ticket.assignee)[0].accountId
            self.assign_issue(issue, user)
            logger.info(f"Assigned {issue}")
        except (JIRAError, IndexError):
            logger.warning(f"Cannot assign {issue}")
        try:
            self.transition_issue(
                issue,
                list(
                    filter(
                        lambda x: ticket.status in x["to"].get("name"),
                        self.transitions(issue),
                    )
                )[0]["id"],
            )
            logger.info(f"Transitioned {issue}")
        except Exception:
            logger.warning("Cannot transition issue")
        for comment in ticket.comments:
            logger.info(f"Adding {comment} in {issue}")
            if comment.text:
                text_with_commenter = (
                    f"{comment.commenter} " f"said: {comment.text}"
                )
                self.add_comment(issue, text_with_commenter)

    def get_issue_from_summary(self, project, summary):
        jql = (
            f'project = "{project}" and summary '
            f'~ "{summary}" ORDER BY created DESC'
        )
        return self.search_issues(jql)

    def search_users(
        self,
        user,
        startAt=0,
        maxResults=50,
        includeActive=True,
        includeInactive=False,
    ):
        """Get a list of user Resources that match the specified search string.

        :param user: a string to match usernames, name or email against.
        :param startAt: index of the first user to return.
        :param maxResults: maximum number of users to return.
                If maxResults evaluates as False, it will try to get all items in batches.
        :param includeActive: If true, then active users are included in the results.
        :param includeInactive: If true, then inactive users are included in the results.
        """
        params = {
            "query": user,
            "includeActive": includeActive,
            "includeInactive": includeInactive,
        }
        return self._fetch_pages(
            User, None, "user/search", startAt, maxResults, params
        )

    def assign_issue(self, issue, assignee):
        """Assign an issue to a user. None will set it to unassigned. -1 will set it to Automatic.

        :param issue: the issue ID or key to assign
        :param assignee: the user to assign the issue to

        :type issue: int or str
        :type assignee: str

        :rtype: bool
        """
        url = (
            self._options["server"]
            + "/rest/api/latest/issue/"
            + str(issue)
            + "/assignee"
        )
        payload = {"accountId": assignee}
        self._session.put(url, data=json.dumps(payload))
        return True

    def create_tickets(self, tickets, project):
        """
        Create JIRA tickets:

        :param list(Ticket) tickets: The tickets to create
        :param str project: The project name
        :return: The list of created JIRA issues
        :rtype: list(jira.issue)
        """
        cur_project = list(
            filter(lambda x: project in x.name, self.projects())
        )[0]

        issues = list()
        for ticket in tickets:
            issues.append(self.create_ticket(ticket, cur_project.id))
        return issues
