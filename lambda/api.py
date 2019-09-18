from errors import SumoException
from sumologic import SumoLogic
import logging
import time
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SumoAPI(object):

    def __init__(self, access_id, access_key, deployment, kvstore):
        self.deployment = deployment
        self.sumologic_cli = SumoLogic(access_id, access_key)
        self.kvstore = kvstore

    def run_saved_search(self, name):
        # saves job id and schedules search
        search_query = self.get_saved_search_by_name(name)
        response = self._run_search(search_query)
        user_data = self.kvstore.get()
        search_jobs = user_data.get("search_jobs", [])
        search_jobs.append({"search_name": name, "job_id": response["id"], "is_aggregate": bool(self._is_aggregate_query(search_query))})
        self.kvstore.save({"search_jobs": search_jobs})

    def run_raw_search(self, search_query, duration):
        sep= '<break time="1s"/>'
        lsep = '<break time="2s"/>'
        # saves job id and schedules search
        response = self._run_search(search_query, duration)
        # user_data = self.kvstore.get()
        # search_jobs = user_data.get("search_jobs", [])
        # search_jobs.append({"search_name": search_query, "job_id": response["id"],
        #                     "is_aggregate": bool(self._is_aggregate_query(search_query))})
        # self.kvstore.save({"search_jobs": search_jobs})
        time.sleep(5)
        response1 = self._get_search_results(response)
        speaktext = "Found %d Results%s" % (len(response1),lsep)
        for i, res in enumerate(response1):
            non_cnt_fields = ", ".join(["%s" % (v) for k, v in res.items() if not self._is_aggregate_query(k)])
            cnt_values = "".join(["%s is %s %s" % (k, v, sep) for k, v in res.items() if self._is_aggregate_query(k)])
            if non_cnt_fields:
                speaktext += "%s for %s%s" % (cnt_values, non_cnt_fields,sep)
            else:
                speaktext += "%s%s" % (cnt_values,sep)
        return "<speak>" + speaktext + "</speak>"


    def get_search_results(self, name=None):
        search_job = self._get_job_id_by_name(name)
        response = self._get_search_results(search_job)
        speaktext = "Found %d Results" % len(response)
        for i, res in enumerate(response):
            speaktext += "Row %d %s" % (i, " ".join(["%s=%s" % (k, v) for k,v in res.items()]))
        return speaktext

    def _get_job_id_by_name(self, name):
        user_data = self.kvstore.get()
        search_jobs = user_data.get("search_jobs", [])
        if len(search_jobs) == 0:
            raise SumoException("No Search job found. Please specify the Scheduled search name")
        if name:
            search_job = list(filter(lambda x: x["search_name"] == name, search_jobs))
            if len(search_job) == 0:
                raise SumoException("No Search job found with %s name" % name)
            else:
                search_job = search_job[0]
        else:
            search_job = search_jobs[0]

        return search_job

    def _run_search(self, query, duration_sec=24*60*60*1000):
        to_time = int(time.time())*1000
        from_time = to_time - duration_sec
        logger.info("to_time >> "+str(to_time))

        logger.info("from_time >> "+str(from_time))
        try:
            response = self.sumologic_cli.search_job(query, fromTime=from_time, toTime=to_time)
            logger.info("schedule job status: %s" % response)
            return response
        except Exception as e:
            if hasattr(e, "response") and e.response.status_code == 401:
                raise SumoException("unable to authenticate")
            elif hasattr(e, "response") and e.response.status_code == 403:
                raise SumoException("you do not have permission")
            elif hasattr(e, "response") and hasattr(e.response, "message"):
                raise SumoException("unable to run search status_code: %s message: %s" % (e.response.status_code, e.response.message))
            else:
                raise SumoException("unknown error")

    def _get_search_results(self, search_job):
        job_id = search_job['id']
        response = self.sumologic_cli.search_job_status({"id": job_id})
        logger.info("job status: %s" % response)
        errors = response.get("pendingErrors", [])
        if len(errors) > 0:
            raise SumoException("Invalid Query with Error: %s" % errors[0])
        else:
            if response.get("recordCount", 0) > 0:
                return self._get_search_records(search_job)
            else:
                return self._get_search_messages(search_job)

    def _get_search_messages(self, search_job):
        '''
        {
            "fields": [
                {
                    "name": "_blockid",
                    "fieldType": "long",
                    "keyField": false
                }
            ],
            "messages": [
                {
                    "map": {
                        "_blockid": "-9223372036615452305",
                        "status_code": "200",
                        "method": "GET",
                        "_messagetime": "1568713340840",
                        "_raw": "49.212.135.76 - - [2019-09-17 09:42:20.840 +0000] \"GET /_js/master.js HTTP/1.1\" 200 2132 \"http://www.bing.com/search?q=sumo%20logic&src=IE-SearchBox&FORM=IE11SR\" \"Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; en-us) AppleWebKit/533.21.1 (KHTML, like Gecko) Chrome/19.0.1084.30 Safari/536.5\"",
                        "_collectorid": "164491766",
                        "_sourceid": "723329913",
                        "_collector": "Labs - Apache",
                        "_messagecount": "314",
                        "_sourcehost": "34.238.197.190",
                        "url": "/_js/master.js",
                        "_messageid": "-9223371714138842310",
                        "_sourcename": "Http Input",
                        "_size": "294",
                        "src_ip": "49.212.135.76",
                        "referrer": "http://www.bing.com/search?q=sumo%20logic&src=IE-SearchBox&FORM=IE11SR",
                        "size": "2132",
                        "_view": "",
                        "_receipttime": "1568713341449",
                        "_sourcecategory": "Labs/Apache/Access",
                        "_format": "t:cache:o:19:l:29:p:yyyy-MM-dd HH:mm:ss.SSSZZZZ",
                        "_source": "Apache Access",
                        "user_agent": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; en-us) AppleWebKit/533.21.1 (KHTML, like Gecko) Chrome/19.0.1084.30 Safari/536.5"
                    }
                }
        }
        '''
        response = self.sumologic_cli.search_job_messages(search_job, limit=5)
        results = []
        for row in response['messages']:
            results.append({"raw": row['map']['_raw'], "message_time": row['map']['_messagetime']})
        return results

    def _get_search_records(self, search_job):
        '''
                {
            "fields": [
                {
                    "name": "_sourcehost",
                    "fieldType": "string",
                    "keyField": true
                },
                {
                    "name": "_count",
                    "fieldType": "int",
                    "keyField": false
                }
            ],
            "records": [
                {
                    "map": {
                        "_count": "231262",
                        "_sourcehost": "34.238.197.190"
                    }
                }
            ]
        }
        '''
        response = self.sumologic_cli.search_job_records(search_job, limit=5)
        results = []
        for row in response['records']:
            res = {}
            for k, v in row['map'].items():
                k = k[1:] if k.startswith('_') else k
                res[k]=v
            results.append(res)
        return results

    def _is_aggregate_query(self, query):
        return re.findall(r'\bavg\b | \bcount\b | \bcount_distinct\b | \bcount_frequent\b | \bfirst\b | \blast\b | \bmin\b | \bmax\b | \bmost_recent\b | \bleast_recent\b | \bpct\b | \bstddev\b | \bsum\b', query, re.I | re.X)

    def get_saved_search_by_name(self, name):
        pass

    def get_panel_by_name(self, panel_name, dashboard_name):
        pass

    def _get_content(self, folder_id):
        pass
        # searches = []
        # panels = []
        # folder = self._get_folder(folder_id)
        # if len(folder.get("children", [])) > 0:
        #     for dash in folder["children"]:
        #         if dash["type"] == "Report":
        #             dashboards.append(dash)
        #         elif dash["type"] == "Search":
        #             searches.append(dash)
        #         elif dash["type"] == "Folder":
        #
        #             d, s = self._get_content(dash)
        #             searches.extend(s)
        #             panels.extend(d)
        #
        # return panels, searches

    def install_app(self):
        pass

    def get_recent_release_docs(self):
        pass

    def get_operator_docs(self):
        pass

    def _get_folder(self):
        pass

    def _get_personal_folder(self):
        response = self.sumologic_cli.get_personal_folder()
        return response.json()['id']

if __name__ == '__main__':
    pass


