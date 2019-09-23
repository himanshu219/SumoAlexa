import decimal
import sys
sys.path.insert(0, '/opt')
import requests
import json
import logging
import time
import re

from errors import SumoException
from sumologic import SumoLogic
import unicodedata
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def slugify(s):
    s = s.decode() if isinstance(s, bytes) else s
    slug = unicodedata.normalize('NFKD', s)
    slug = re.sub(r'[^A-Za-z0-9]+', '-', slug).strip('-')
    slug = re.sub(r'[-]+', '-', slug)
    slug = slug.encode('ascii', 'ignore').lower()
    return slug

def matchstr(first, second):
    return slugify(first) == slugify(second)

def isnumber(val):
    if isinstance(val, (float, int, decimal.Decimal)):
        return True
    try:
        float(val)
        return True
    except:
        pass
    return False


class SumoAPI(object):

    urls = {
        "long": "https://long-www.sumologic.net",
        "nite": "https://nite-www.sumologic.net",
        'stag': "https://stag-www.sumologic.net",
        "us1": "https://service.sumologic.com",
        "us2": "https://service.us2.sumologic.com",
        "dub": "https://service.eu.sumologic.com",
        "fed": "https://service.fed.sumologic.com",
        "fra": "https://service.de.sumologic.com",
        "syd": "https://service.au.sumologic.com",
        "mon": "https://service.ca.sumologic.com",
        "tky": "https://service.jp.sumologic.com"
    }
    api_urls = {
        "long": "https://long-api.sumologic.net/api",
        "nite": "https://nite-api.sumologic.net/api",
        'stag': "https://stag-api.sumologic.net/api",
        "us1": "https://api.sumologic.com/api",
        "us2": "https://api.us2.sumologic.com/api",
        "dub": "https://api.eu.sumologic.com/api",
        "fed": "https://api.fed.sumologic.com/api",
        "fra": "https://api.de.sumologic.com/api",
        "syd": "https://api.au.sumologic.com/api",
        "mon": "https://api.ca.sumologic.com/api",
        "tky": "https://api.jp.sumologic.com/api"
    }

    def __init__(self, access_id, access_key, deployment, email, password, kvstore):
        self.deployment = deployment
        self.sumologic_cli = SumoLogic(access_id, access_key, endpoint=self.api_urls.get(deployment, "us1"))
        self.kvstore = kvstore
        self.session=None
        self.headers=None
        self.email = email
        self.password = password
        self._login()

    def _get_aggregate_field(self, res):
        '''
            SVD count is 10
            multiple fields count is 10 for  <collectorname>
                key matches count makes it potential find first key with non numeric value
            no count field like first collector is <>, key is value  pick first field
        '''

        agg_fld = agg_fld_without_count_in_key = None
        has_cnt_in_key = lambda key: re.findall(
            r'\bavg\b | \bcount\b | \bcount_distinct\b | \bcount_frequent\b | \bmin\b | \bmax\b | \bpct\b | \bstddev\b | \bsum\b',
            key, re.I | re.X)
        for k, v in res.items():
            if not isnumber(v):
                if not agg_fld:
                    agg_fld = k # first field without numeric
                if not agg_fld_without_count_in_key and has_cnt_in_key(k.replace("_", " ")):
                    agg_fld_without_count_in_key = k # first field without numeric and colname does not contains count
                    break

        return  agg_fld_without_count_in_key if agg_fld_without_count_in_key else agg_fld


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
        speaktext = "Found %d Results%s \n" % (len(response1),lsep)
        num_rows = len(response1)
        if num_rows > 0:
            for_field = self._get_aggregate_field(response1[0])
            print("For Field", for_field)
            for i, row in enumerate(response1):
                for k, v in row.items():
                    row[k] = v
                if for_field:
                    for_text = row[for_field]
                    cnt_values = "".join(["%s is %s," % (k, v) for k, v in row.items() if k != for_field])
                    speaktext += "%s for %s.%s\n" % (cnt_values.strip(","), for_text, sep)
                else:
                    cnt_values = "".join(["%s is %s," % (k, v) for k, v in row.items()])
                    if num_rows == i+1:
                        # last row
                        speaktext += "%s\n" % (cnt_values)
                    else:
                        speaktext += "%s. Next Row %s\n" % (cnt_values, sep)
        print("query output",speaktext)
        return "<speak>" + speaktext + "</speak>"


    def run_saved_search(self, name, duration):
        # saves job id and schedules search
        folder_id = self._get_personal_folder()
        search = self._get_saved_search_recursively(folder_id, name)
        if search:
            search_id = search['externalId']
            search_query = self._get_saved_search_query(search_id)
            return self.run_raw_search(search_query, duration)
        else:
            return "<speak>Saved Search with name %s not found</speak>" % name
        # response = self._run_search(search_query)
        # user_data = self.kvstore.get()
        # search_jobs = user_data.get("search_jobs", [])
        # search_jobs.append({"search_name": name, "job_id": response["id"], "is_aggregate": bool(self._is_aggregate_query(search_query))})
        # self.kvstore.save({"search_jobs": search_jobs})

    def run_search_from_panel(self, panel_name, dashboard_name, duration):
        folder_id = self._get_personal_folder()
        panel = self._get_panels_recursively(folder_id, panel_name, dashboard_name)
        if panel:
            search_query = panel['queryString']
            return self.run_raw_search(search_query, duration)
        else:
            return "<speak>Panel with name %s in dashboard %s not found</speak>" % (panel_name, dashboard_name)

    # def get_search_results(self, name=None):
    #     search_job = self._get_job_id_by_name(name)
    #     response = self._get_search_results(search_job)
    #     speaktext = "Found %d Results" % len(response)
    #     for i, res in enumerate(response):
    #         speaktext += "Row %d %s" % (i, " ".join(["%s=%s" % (k, v) for k,v in res.items()]))
    #     return speaktext
    #
    # def _get_job_id_by_name(self, name):
    #     user_data = self.kvstore.get()
    #     search_jobs = user_data.get("search_jobs", [])
    #     if len(search_jobs) == 0:
    #         raise SumoException("No Search job found. Please specify the Scheduled search name")
    #     if name:
    #         search_job = list(filter(lambda x: x["search_name"] == name, search_jobs))
    #         if len(search_job) == 0:
    #             raise SumoException("No Search job found with %s name" % name)
    #         else:
    #             search_job = search_job[0]
    #     else:
    #         search_job = search_jobs[0]
    #
    #     return search_job

    def _run_search(self, query, duration_sec=24*60*60*1000):
        logger.info("QUERY >> " + query)
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
        response = self.sumologic_cli.search_job_messages(search_job, limit=5)
        results = []
        for row in response['messages']:
            results.append({"raw": row['map']['_raw'], "message_time": row['map']['_messagetime']})
        return results

    def _get_search_records(self, search_job):
        response = self.sumologic_cli.search_job_records(search_job, limit=5)
        results = []
        for row in response['records']:
            res = {}
            for k, v in row['map'].items():
                k = k[1:] if k.startswith('_') else k
                res[k]=v
            results.append(res)
        return results

    def _get_saved_search_query(self, searchId):
        url = self.urls.get(self.deployment) + '/json/v1/savedsearch/getSingle/table?searchId=' + str(searchId)
        response = self.session.get(url, headers=self.headers)
        result = response.json()
        query = result["query"]["queryString"]
        #timeRange = result["query"]["timeRange"]
        return query

    def _get_saved_search_recursively(self, folder_id,  name):
        content = None
        folders = []
        folder = self.get_folder(folder_id)
        if len(folder.get("children", [])) > 0:
            for childdict in folder["children"]:
                for _, child in childdict.items():
                    if child["type"] == "searchReference" and matchstr(child['name'], name):
                        content = child
                    elif child["type"] == "folder":
                        folders.append(child)

        if (not content) and folders:
            for folder in folders:
                content = self._get_saved_search_recursively(folder['id'], name)
                if content:
                    break
        return content

    def _get_dashboard(self, dash_access_key):
        url = self.urls.get(self.deployment) + '/json/v2/reports/' + str(dash_access_key)
        response = self.session.get(url, headers=self.headers)
        dashboard = response.json()
        return dashboard

    def _get_panel_from_dashboard(self, dash_access_key, panel_name):
        content = None
        dashboard = self._get_dashboard(dash_access_key)
        for panel in dashboard['panels']:
            if matchstr(panel['title'], panel_name):
                content = panel
                break
        return content

    def _get_panels_recursively(self, folder_id, panel_name, dashboard_name):
        # if multiple same dashboards returns first matched
        content = None
        folders = []
        folder = self.get_folder(folder_id)
        if len(folder.get("children", [])) > 0:
            for childdict in folder["children"]:
                for _, child in childdict.items():
                    if child["type"] == "interactiveReportReference" and matchstr(child['name'], dashboard_name):
                        content = self._get_panel_from_dashboard(child['accessKey'], panel_name)
                    elif child["type"] == "folder":
                        folders.append(child)

        if (not content) and folders:
            for folder in folders:
                content = self._get_panels_recursively(folder['id'], panel_name, dashboard_name)
                if content:
                    break
        return content

    def _get_personal_folder(self):
        response = self.sumologic_cli.get_personal_folder()
        return int(response.json()['id'], 16)

    def _login(self):
        self.session = requests.session()

        self.headers = {
            'Pragma': 'no-cache',
            'Origin': self.urls.get(self.deployment),
            'Accept-Encoding': 'gzip, deflate, br',
            'ApiSession': 'null',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/61.0.3163.91 Safari/537.36',
            'Content-Type': 'application/json',
            'Accept-Language': 'en-GB,en-US;q=0.8,en;q=0.6',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Cache-Control': 'no-cache',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Referer': self.urls.get(self.deployment) + '/ui/',
        }

        data = {"email": self.email, "password": self.password}
        req = self.session.post(self.urls.get(self.deployment) + '/json/v1/authentication/loginwithcredentials',
                                headers=self.headers, data=json.dumps(data))
        response = json.loads(req.text)
        self.headers['ApiSession'] = response['apiSessionId']
        logger.info('Login is successful for %s', self.email)

    def get_folder(self, folder_id):
        url = self.urls.get(self.deployment) + '/json/v1/content/folder/%s' % (folder_id)
        response = self.session.get(url, headers=self.headers)
        result = response.json()
        return result['folder']

if __name__ == '__main__':
    from lambda_function import access_id ,access_key,deployment,email,password
    api=SumoAPI(access_id, access_key, deployment, email, password, "")

    duration = 1*60*60*1000
    # print(api.run_saved_search("Threats Over Time - VPC", duration))
    # print(api.run_search_from_panel('Total Alerts', 'Netskope - Alert Overview', duration))
    # print(api.run_search_from_panel('Failed Authentications', 'MongoDB Atlas - Audit', duration))
    print(api.run_search_from_panel('lag by node', 'US2 Search Lag Playbook', duration))
    # print(api.run_raw_search())