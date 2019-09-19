import jenkins
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class JenkinsApi(object):

    def __init__(self, username, password):
        self.username=username
        self.password=password
        self.server=None
        self.jobs=None
        self.broken=None



    def login(self):
        self.server = jenkins.Jenkins('https://jenkins.kumoroku.com/', username=self.username, password=self.password)

    def find_all_failed_jobs(self):
        self.broken= self.server._get_view_jobs("Broken")
        master=stag=e2e=it=release=flow=0
        for job in self.broken:
            print("job>   "+str(job))
            if("Master" in job['fullname']):
                master+=1
            else:
                stag+=1

            if("Flow" in job['fullname']):
                flow+=1
            elif("E2E" in job['fullname']):
                e2e+=1
            elif("Release" in job['fullname'] ):
                release+=1
            else:
                it+=1

        speak= "There are "+str(master)+ " failing Jenkins Jobs in Master " \
                                    "and "+ str(stag)+" in stag. Out of which "+str(it)+" are Integration tests " \
                                                                              ""+str(e2e)+" are End to End " +str(release)+ " are Release and "+str(flow)+ " Flow jobs"
        print("SPEAK>> "+speak)

if __name__ == '__main__':
    api = JenkinsApi("", "")
    api.login()
    api.find_all_failed_jobs()
