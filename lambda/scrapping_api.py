import datetime
import sys
sys.path.insert(0, '/opt')

import bs4
import requests

from utils import get_sep


class DochubPageAPI(object):

    def fetch_page(self):
        response = requests.get("https://help.sumologic.com/Release-Notes/Service-Release-Notes")
        if response.ok:
            soup = bs4.BeautifulSoup(response.content, features="html.parser")
            section = soup.find_all('div', {'class': 'mt-section'}) # gives all section with dates
            if len(section) > 0:
                return section
            else:
                return None
        else:
            return None

    def get_latest_release_notes(self):
        sections = self.fetch_page()
        if sections:
            first_section = sections[0]
            date = first_section.find("h2", class_="editable").text
            text = "Last Release was on %s %s" % (date, get_sep(2))
            feature_section = first_section.find_all("div", class_="mt-section")
            for child in feature_section:
                title = child.find("h4", class_="editable").text
                text += "In %s following features were released %s" % (title,get_sep(2))
                for feature in child.find_all("p"):
                    line = feature.text.strip()
                    if line:
                        line = line.encode('utf-8', 'ignore').decode("utf-8")
                        first_line = line.split(".")[0]
                        text += "%s %s" % (first_line, get_sep(1))
            return "<speak>" + text + "</speak>"
        else:
            return "Sorry! unable to fetch Release notes"


class StatusPageAPI(object):

    def fetch_page(self,deployment='us1'):
        status_url = {
            "syd": "https://status.au.sumologic.com",
            "dub": "https://status.eu.sumologic.com",
            "fra": "https://status.de.sumologic.com",
            "fed": "https://status.fed.sumologic.com",
            "jp": "https://status.jp.sumologic.com",
            "tky": "https://status.jp.sumologic.com",
            "mon": "https://status.ca.sumologic.com",
            "us1": "https://status.us1.sumologic.com",
            "us2": "https://status.us2.sumologic.com",
        }

        response = requests.get(status_url[deployment])
        if response.ok:
            soup = bs4.BeautifulSoup(response.content, features="html.parser")
            section = soup.find_all('div', {'class': 'status-day'})  # gives all section with dates
            if len(section) > 0:
                return section
            else:
                return None
        else:
            return None

    def get_service_status(self, deployment='syd'):
        day = datetime.datetime.now().day
        sections = self.fetch_page(deployment)
        text = "Sorry! unable to fetch Release notes"
        if sections:
            for section in sections:
                day_val = section.find('var').text.strip()
                print(day_val, str(day))
                if day_val == str(day):
                    date_val = section.find('div', class_="date").text
                    text = "On %s %s" % (date_val, get_sep(1))
                    incident_container = section.find('div', class_="incident-container")
                    if incident_container:
                        title = incident_container.find('div', class_="incident-title").text
                        updates_container = incident_container.find('div', class_="updates-container")
                        latest_update = updates_container.find('div', class_="update")
                        strong_tag = latest_update.find_all('strong')[0]
                        print(strong_tag.text, strong_tag.next_sibling)
                        status_text = strong_tag.text.strip()
                        updates_text = strong_tag.next_sibling.replace("-","").strip()
                        text += "Current Status for %s is %s. %s" % (title, status_text, updates_text)
                    else:
                        text += section.find('p').text
                    break

        return "<speak>" + text + "</speak>"