from jira import JIRA
# import functools


def capture_err(f):

    # @functools.wraps
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            print(e)
            return {}

    return wrapper

class JiraAPI(object):

    def __init__(self, username, password):
        self.client = JIRA('https://jira.kumoroku.com/jira/', basic_auth=(username, password))

    @capture_err
    def get_issue_by_id(self, jira_id):
        issue = self.client.issue(jira_id)
        print(issue.fields.project.key)  # 'JRA'
        print(issue.fields.issuetype.name)  # 'New Feature'
        print(issue.fields.reporter.displayName)  # 'Mike Cannon-Brookes [Atlassian]'
        print(issue.fields.project.name)
        return {'id': jira_id, 'name': issue.fields.summary, 'component': issue.fields.project.name}

    @capture_err
    def get_blocker_issues(self, branch, limit=5):
        branch = "19.%s" % branch
        query = 'project in (10000, 10640) AND status != Closed AND (affectedVersion in (%s) OR fixVersion in (%s)) AND type in (Bug, "Bug for User Story", "Customer Support Issue") AND priority = Blocker ORDER BY priority DESC, status ASC, created DESC' % (branch, branch)
        issues_in_proj = self.client.search_issues(query)
        return {'count': len(issues_in_proj), 'issues': [{'assignee': issue.fields.assignee.name, 'summary': issue.fields.summary} for issue in issues_in_proj][:limit]}

    @capture_err
    def get_blocker_issues_by_project(self, name, limit=5):
        query = 'component=\"%s\" AND project in (10000, 10640) AND status != Closed AND type in (Bug, "Bug for User Story", "Customer Support Issue") AND priority = Blocker ORDER BY priority DESC, status ASC, created DESC' % (name)
        print(query)
        issues_in_proj = self.client.search_issues(query)
        return {'count': len(issues_in_proj), 'issues': [issue.fields.summary for issue in issues_in_proj][:limit]}

    @capture_err
    def get_blocker_issues_by_user(self, user, limit=5):
        query = 'assignee=%s AND project in (10000, 10640) AND status != Closed AND type in (Bug, "Bug for User Story", "Customer Support Issue") AND priority = Blocker ORDER BY priority DESC, status ASC, created DESC' % (user)
        issues_in_proj = self.client.search_issues(query)
        return {'count': len(issues_in_proj), 'issues': [issue.fields.summary for issue in issues_in_proj][:limit]}

    @capture_err
    def get_latest_reported_issues(self, limit=3):
        return [{'status': issue.fields.status, 'summary': issue.fields.summary} for issue in self.client.search_issues('reporter = currentUser() order by created desc', maxResults=limit)]





