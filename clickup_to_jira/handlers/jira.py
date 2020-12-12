import json
from logging import getLogger

from jira import JIRA
from jira.exceptions import JIRAError
from jira.resources import User

from clickup_to_jira.utils import get_item_from_user_input

logger = getLogger(__name__)

DEFAULT_ISSUE_TYPE = "Story"


class JIRAHandler(JIRA):
    """
    Class responsible for adding Ticket to JIRA.
    """

    status_mappings = {}
    type_mappings = {}

    def create_jira_issues(self, tickets):
        """
        Create JIRA issues:

        :param list(Ticket) tickets: The tickets to create
        :return: The list of created JIRA issues
        :rtype: list(jira.issue)
        """
        # Create type mappings from tickets
        cur_project = get_item_from_user_input("project", self.projects())
        self.type_mappings = self.create_type_mappings(tickets)
        logger.info(self.type_mappings)

        # Create all tickets
        issues = list()
        for ticket in tickets:
            issues.append(self.create_jira_issue(ticket, cur_project.id))
        return issues

    def create_jira_issue(self, ticket, project):
        """
        Create a JIRA issue.

        :param Ticket ticket: The ticket to create
        :param str project: The project name
        :return: The new ticket
        :rtype: jira.issue
        """
        logger.info(f"Creating {ticket.title} in JIRA.")
        # Check issue already exists
        try:
            if self.get_issue_from_summary(project, ticket.title):
                logger.warning(f"Ticket {ticket.title} already exists.")
                return
        except JIRAError as e:
            logger.warning(e)
            return

        # Create issue in JIRA
        issue = self.create_base_jira_issue(ticket, project)
        if not issue:
            logger.exception(f"Cannot create issue from {ticket}.")
            return

        # Assign issue in proper user
        self.assign_issue_to_user(issue, ticket)

        # Transition issue to proper status
        self.transition_issue_to_proper_status(issue, ticket)

        # Add comments in ticket
        self.add_comments(issue, ticket)

    def create_base_jira_issue(self, ticket, project):
        """
        Create a JIRA issue given the ticket and the JIRA project.

        :param Ticket ticket: The ticket to create to JIRA
        :param str project: The project name to add the ticket to
        :return: The JIRA Issue
        :rtype: Jira.issue
        """
        try:
            # Populate basic data for ticket creation
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

            # Handle case where issue is subtasks
            parent_list = self.get_issue_from_summary(project, ticket.parent)
            if parent_list:
                logger.info(f"Ticket {ticket.title} has parent")
                issue_data["parent"] = {"id": parent_list[0].id}

            # Create the ticket
            return self.create_issue(**issue_data)
        except JIRAError:
            logger.exception("Cannot create issue. Move on")
            return None

    def assign_issue_to_user(self, issue, ticket):
        """
        Assign JIRA issue to a user.

        :param jira.issue issue: The JIRA issue
        :param Ticket ticket: The Ticket to retrieve the assignee from
        """
        try:
            user = self.search_users(user=ticket.assignee)[0].accountId
            self.assign_issue(issue, user)
            logger.info(f"Assigned {issue}")
        except (JIRAError, IndexError):
            logger.warning(f"Cannot assign {issue}")

    def transition_issue_to_proper_status(self, issue, ticket):
        """
        Transition JIRA issue to the desired status.

        :param jira.issue issue: The JIRA issue
        :param Ticket ticket: The Ticket to retrieve the assignee from
        """
        if ticket.status not in self.status_mappings.keys():
            try:
                self.update_status_mappings(ticket, issue)
            except JIRAError:
                logger.warning("Cannot transition ticket")
                return
        try:
            self.transition_issue(
                issue,
                self.status_mappings[ticket.status],
            )
            logger.info(f"Transitioned {issue}")
        except (JIRAError, IndexError, KeyError, AttributeError):
            logger.warning("Cannot transition issue")

    def update_status_mappings(self, ticket, issue):
        """
        Update status mappings from user input.

        :param jira.issue issue: The JIRA issue
        :param Ticket ticket: The Ticket to retrieve the assignee from
        """
        # Populate jira statuses for specific Issue
        jira_statuses = list(
            set(
                [
                    transition["to"].get("name")
                    for transition in self.transitions(issue)
                ]
            )
        )
        # Check if mappings already exists for ticket status
        if ticket.status in self.status_mappings.keys():
            return

        # Read JIRA status
        jira_status = input(
            f"Please provide a mapping for {ticket.status}."
            f"\nEligible options are {jira_statuses} :\n"
        )

        # Add mapping if not exists
        if jira_status not in jira_statuses:
            while True:
                jira_status = input(
                    f"{jira_status} is not a valid choice. "
                    f"Please provide one of {jira_statuses} :\n"
                )
                if jira_status in jira_statuses:
                    self.status_mappings[ticket.status] = jira_status
                    break
        else:
            self.status_mappings[ticket.status] = jira_status

    def create_type_mappings(self, tickets):
        """
        Create mappings between ClickUp labels and Jira Ticket types.

        :param list(Ticket) tickets: The tickets to create
        :return: The type mappings
        :rtype: dict
        """
        # Populate ClickUp labels found and JIRA types available
        click_up_labels = list(
            set(
                [
                    ticket_type
                    for ticket in tickets
                    for ticket_type in ticket.type.split(",")
                ]
            )
        )
        jira_types = list(
            set([issue_type.name for issue_type in self.issue_types()])
        )
        print(jira_types)

        # Create default mappings
        try:
            default_jira_type = list(
                filter(lambda x: DEFAULT_ISSUE_TYPE == x, jira_types)
            )[0]
        except IndexError:
            default_jira_type = jira_types[0]
        default_mapping = {
            click_up_label: default_jira_type
            for click_up_label in click_up_labels
        }

        # Select between custom or standard mappings
        selection = input(
            f"Default mapping is : {default_mapping}"
            f"\nPress Y if you want to use this mapping "
            f"or N if you want to assign a mapping of your own :\n"
        )

        # Handle all selections
        if selection not in ["N", "Y"]:
            while True:
                selection = input(
                    f"{selection} is not a valid choice. "
                    f"Please write Y on N :\n"
                )
                if selection == "N":
                    return self.__compute_type_mappings(
                        click_up_labels, jira_types
                    )
                elif selection == "Y":
                    return default_mapping

        elif selection == "Y":
            return default_mapping
        else:
            return self.__compute_type_mappings(click_up_labels, jira_types)

    @staticmethod
    def __compute_type_mappings(click_up_labels, jira_types):
        """
        Compute the type mappings.

        :param list(str) click_up_labels: The ClickUp labels
        :param list(str) jira_types: The JIRA types
        :return: The computed mappings
        :rtype: dict
        """
        mappings = {}
        for click_up_label in click_up_labels:
            printable_label = click_up_label if click_up_label else "''"
            jira_type = input(
                f"Please provide a mapping for {printable_label}."
                f"\nEligible options are {jira_types} :\n"
            )
            if jira_type not in jira_types:
                while True:
                    jira_type = input(
                        f"{jira_type} is not a valid choice. "
                        f"Please provide on of {jira_types} :\n"
                    )
                    if jira_type in jira_types:
                        mappings[click_up_label] = jira_type
                        break
            else:
                mappings[click_up_label] = jira_type
        return mappings

    def add_comments(self, issue, ticket):
        """
        Add comments to JIRA Issue.

        :param jira.issue issue: The issue to add comments to
        :param Ticket ticket: The ticket to read comments from
        """
        for comment in ticket.comments:
            logger.info(f"Adding {comment} in {issue}")
            print(comment.text)
            if comment.text:
                text_with_commenter = (
                    f"{comment.commenter} said: {comment.text}"
                )
                try:
                    self.add_comment(issue, text_with_commenter)
                except JIRAError:
                    logger.warning(f"Failed to add {comment} in {issue}")
                    continue

    def get_issue_from_summary(self, project, summary):
        """
        Get issue from given summary.

        :param str project: Project to search in
        :param str summary: The summary string
        :return: The JIRA issue
        :rtype: jira.issue
        """
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
        """
        Get a list of user Resources that match the specified search string.

        :param str user: a string to match usernames, name or email against.
        :param int startAt: index of the first user to return.
        :param int maxResults: maximum number of users to return. If
            maxResults evaluates as False, it will try to get all items
            in batches.
        :param bool includeActive: If true, then active users are included in
            the results.
        :param bool includeInactive: If true, then inactive users are included
            in the results.
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
        """
        Assign an issue to a user.

        None will set it to unassigned. -1 will set it to Automatic.

        :param int|str issue: the issue ID or key to assign
        :param str assignee: the user to assign the issue to
        :rtype: bool
        :rtype: Assignment succeeded
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
