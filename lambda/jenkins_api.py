import jenkins

class JenkinsAPI(object):

    def __init__(self, username, password):
        self.username=username
        self.password=password
        self.server=None
        self.login()

    def login(self):
        self.server = jenkins.Jenkins('https://jenkins.kumoroku.com/', username=self.username, password=self.password)

    def find_all_failed_jobs(self):
        broken = self.server._get_view_jobs("Broken")
        master = stag = e2e = it = release = flow = 0
        for job in broken:
            if "Master" in job['fullname']:
                master += 1
            else:
                stag += 1

            if "Flow" in job['fullname']:
                flow += 1
            elif "E2E" in job['fullname']:
                e2e += 1
            elif "Release" in job['fullname'] :
                release += 1
            else:
                it += 1

        return {
            "failing_master_jobs": master,
            "failing_stag_jobs": stag,
            "failing_e2e_jobs": e2e,
            "failiing_it_jobs": it,
            "failing_release_jobs": release,
            "failing_flow_jobs": flow
        }


if __name__ == '__main__':
    api = JenkinsAPI("", "")
    api.login()
    api.find_all_failed_jobs()
