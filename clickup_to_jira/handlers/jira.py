from jira import JIRA


class JIRAHandler(JIRA):
    def create_ticket(self, ticket, project):
        """
        Create a JIRA ticket.

        :param Ticket ticket: The ticket to create
        :param str project: The project name
        :return: The new ticket
        :rtype: JIRA.issue
        """
        issue_data = {
            "project": project,
            "issuetype": "Story",
            "summary": ticket.name,
            "description": ticket.description,
        }
        return self.create_issue(**issue_data)

    def create_tickets(self, tickets, project):
        """
        Create JIRA tickets:

        :param list(Ticket) tickets: The tickets to create
        :param str project: The project name
        :return: The list of created JIRA issues
        :rtype: list(jira.issue)
        """
        velvont_project = list(
            filter(lambda x: "ChannelManager" in x.name, self.projects())
        )[0]

        issues = list()
        for ticket in tickets:
            issues.append(self.create_ticket(ticket, velvont_project))
        return issues
