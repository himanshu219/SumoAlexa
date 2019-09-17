from sumologic import SumoLogic

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SumoAPI(object):

    def __init__(self, access_id, access_key, deployment):
        self.deployment = deployment
        self.sumologic_cli = SumoLogic(access_id, access_key)

    def run_saved_search(self, query):
        pass

    def get_search_results(self):
        pass

    def get_matched_saved_search(self, query):
        pass

    def get_matched_panel_query(self, query, appname):
        pass

    def _get_content(self):
        pass

    def _run_search(self, query, duration_sec=24*60*60*1000):
        to_time = int(time.time())*1000
        from_time = to_time - duration_sec
        try:
            response = self.sumologic_cli.search_job(query, fromTime=from_time, toTime=to_time)
            logger.info("schedule job status: %s" % response)

        except Exception as e:
            if hasattr(e, "response") and e.response.status_code == 401:
                raise Exception("unable to authenticate")
            elif hasattr(e, "response") and e.response.status_code == 403:
                raise Exception("you do not have permission")
            else:
                raise Exception("unable to run search")

    def import_content(self):
        pass

    def get_recent_release_docs(self):
        pass

    def get_operator_docs(self):
        pass


if __name__ == '__main__':
    access_id =
    access_key =


