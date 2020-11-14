import json
from logging import getLogger

from jira import JIRA
from jira.exceptions import JIRAError
from jira.resources import User

logger = getLogger(__name__)


class JIRAHandler(JIRA):
    status_mappings = {}
    type_mappings = {}

    def create_type_mappings(self, tickets):
        """
        Create mappings between clickup labels and Jira Ticket types.

        :param list(Ticket) tickets: The tickets to create
        """
        clickup_labels = list(
            set(
                [
                    ticket_type
                    for ticket in tickets
                    for ticket_type in ticket.type.split(",")
                ]
            )
        )
        jira_statuses = list(
            set([issue_type.name for issue_type in self.issue_types()])
        )
        try:
            default_jira_type = list(
                filter(lambda x: "Story" == x, jira_statuses)
            )[0]
        except KeyError:
            default_jira_type = jira_statuses[0]
        default_mapping = {
            clickup_label: default_jira_type
            for clickup_label in clickup_labels
        }
        logger.info(f"Default Mapping : {default_mapping}")
        selection = input(
            f"Default mapping is : {default_mapping}"
            f"\nPress Y if you want to use this mapping "
            f"or N if you want to assign a mapping of your own."
        )

        if selection not in ["N", "Y"]:
            while True:
                selection = input(
                    f"{selection} is not a valid choice. Please write Y on N."
                )
                if selection == "N":
                    return self.__compute_type_mappings(
                        clickup_labels, jira_statuses
                    )
                elif selection == "Y":
                    return default_mapping

        elif selection == "Y":
            return default_mapping
        else:
            return self.__compute_type_mappings(clickup_labels, jira_statuses)

    def __compute_type_mappings(self, clickup_labels, jira_statuses):
        mappings = {}
        for clickup_label in clickup_labels:
            printable_label = clickup_label if clickup_label else "''"
            jira_status = input(
                f"Please provide a mapping for {printable_label} : "
                f"\nEligible options are {jira_statuses}"
            )
            if jira_status not in jira_statuses:
                while True:
                    jira_status = input(
                        f"{jira_status} is not a valid choice. "
                        f"Please provide on of {jira_statuses}."
                    )
                    if jira_status in jira_statuses:
                        mappings[clickup_label] = jira_status
                        break
            else:
                mappings[clickup_label] = jira_status
        return mappings

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
        self.type_mappings = self.create_type_mappings(tickets)
        logger.info(self.type_mappings)

        issues = list()
        for ticket in tickets:
            issues.append(self.create_ticket(ticket, cur_project.id))
        return issues

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
            "issuetype": {
                "name": self.type_mappings[ticket.type.split(",")[0]]
            }
            if not ticket.parent
            else {"name": "Subtask"},
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
        issues = self.search_issues(jql)
        proper_issues = [
            issue for issue in issues if issue.fields.summary == summary
        ]
        return proper_issues

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
