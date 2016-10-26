#!/usr/bin/python
import yaml
import requests
requests.packages.urllib3.disable_warnings()

import time
import lxml.etree
import requests
import cachetools
from time import strftime
from apscheduler.schedulers.background import BackgroundScheduler
# import slackbot.bot
import os
# import peewee
from playhouse.postgres_ext import PostgresqlExtDatabase

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(BASE_DIR, '../config.yml')
with open(CONFIG, 'r') as fptr:
    cfg = yaml.load(fptr.read())
DBUSER = cfg['dbuser']
DBPASS = cfg['dbpass']
DB = cfg['db']
MULTCO_TOKEN = cfg['multco_token']
MULTCO_API = 'https://api.multco.us/bridges'

psql_db = PostgresqlExtDatabase(DB, user=DBUSER, password=DBPASS)

ATOM_NS = "{http://www.w3.org/2005/Atom}"
CAP_NS = "{urn:oasis:names:tc:emergency:cap:1.1}"
NWS_FEED_URL = "https://alerts.weather.gov/cap/us.php?x=0"
# NWS_FEED_URL = 'http://alerts.weather.gov/cap/or.php?x=0' # OR only


class NOAAAlert(object):
    """ This holds the stuff we need to care about in a NWS/NOAA alert """
    def __init__(
            self, id, title, event, details, expires, link, fips_codes,
            ugc_codes):
        self._id = id
        self._title = title
        self._event = event
        self._details = details
        self._expires = expires
        self._link = link
        self._fips_codes = fips_codes
        self._ugc_codes = ugc_codes
        self._checked = False  # have we examined this alert for notifications
        self._notified = False  # have we sent a notification about this alert

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @property
    def details(self):
        return self._details

    @property
    def expires(self):
        return self._expires

    @property
    def link(self):
        return self._link

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, value):
        self._checked = value

    @property
    def notified(self):
        return self._notified

    @notified.setter
    def notified(self, value):
        self._notified = value

    def __repr__(self):
        return "id: {0}\ntitle {1}\nevent: {2}\ndetails: {3}\n\
expires: {4}\nlink: {5}\nlink: {6}\nfips: {7}\nugc: {8}".format(
            self._id, self._title, self._event, self._details, self._link,
            self._expires, self._link, self._fips_codes, self._ugc_codes)


class AlertFetcher(object):
    """ Fetch some alerts from NOAA"""

    def __init__(self):
        # TODO populate these from chats
        self._fips_codes = ['041005',
                            '041051',
                            '041067',
                            '054103',
                            '041035']  # klamath for testing
        self._ugc_codes = []
        self.alert_cache = cachetools.TTLCache(maxsize=1000, ttl=600)
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self._no_alerts = False

    def fetch_feed(self):
        """ Fetch NOAA alerts xml feed """
        response = requests.get(NWS_FEED_URL)
        tree = lxml.etree.fromstring(response.text.encode('utf-8'))

        for entry_el in tree.findall(ATOM_NS + 'entry'):
            entry_id = entry_el.find(ATOM_NS + 'id').text
            title = entry_el.find(ATOM_NS + 'title').text
            if title == "There are no active watches, warnings or advisories":
                if not self._no_alerts:
                    # TODO notify about 'no active alerts'
                    print "There are no active alerts at {0}".format(
                        strftime("%Y-%m-%d %H:%M"))
                    self._no_alerts = True
                return
            self._no_alerts = False
            expires_text = entry_el.find(CAP_NS + 'expires').text
            expires_text
            url = entry_el.find(ATOM_NS + 'link').attrib['href']
            fips_list, ugc_list = self.parse_geocode_from_entry(entry_el)
            event, special_severe = self.handle_special_severe(entry_el)

            alert = NOAAAlert(
                entry_id, title, event, ', '.join(
                    special_severe), expires_text, url, fips_list, ugc_list)
            # TODO to give this entry a TTL of (expiry - now) seconds
            if alert.id in self.alert_cache:
                pass
            else:
                self.alert_cache[alert.id] = alert

        self.check_alerts()

    def handle_special_severe(entry):
        # TODO check if there are more of these that we should care about
        severe_special_types = ['Thunderstorm',
                                'Strong Storm',
                                'Wind', 'Rain',
                                'Hail',
                                'Tornado',
                                'Flood']
        if entry.find(CAP_NS + 'event') is not None:
            event = entry.find(CAP_NS + 'event').text
        else:
            event = None
        special_severe = []
        if event in ('Severe Weather Statement',
                     'Special Weather Statement'):
            summary = entry.find(ATOM_NS + 'summary').text.upper()
            for item in severe_special_types:
                if item.upper() in summary:
                    special_severe.append(item)
        return (event, special_severe)

    def parse_geocode_from_entry(self, entry):
        """ Parse the FIPS6 and UGC geocodes from a NOAA feed entry """
        geocode_element = entry.find(CAP_NS + 'geocode')
        fips_list = []
        ugc_list = []

        if geocode_element is not None:
            for value_name_element in geocode_element.findall(
                    ATOM_NS + 'valueName'):
                if value_name_element.text == "FIPS6":
                    fips_element = value_name_element.getnext()
                    if (fips_element is not None
                            and fips_element.text is not None):
                        fips_list = fips_element.text.split(' ')
                elif value_name_element.text == 'UGC':
                    ugc_element = value_name_element.getnext()
                    if (ugc_element is not None
                            and ugc_element.text is not None):
                        ugc_list = ugc_element.text.split(' ')
        return fips_list, ugc_list

    def fetch_details(self, alert):
        """ Fetch details for a specific alert """
        # TODO maybe prettify this
        print "fetching details from  {0}".format(alert.link)
        # detail_response = requests.get(alert.link)
        # print detail_response.text.encode('utf-8')

    def check_alerts(self):
        checked_cached_alerts = 0
        previously_checked_alerts = 0
        alerts_to_update = {}
        for alert_id in self.alert_cache:
            checked_cached_alerts += 1
            alert = self.alert_cache[alert_id]
            if alert.checked:
                previously_checked_alerts += 1
            else:
                fips_match = set(
                    alert._fips_codes).intersection(self._fips_codes)
                alert.checked = True
                if len(fips_match) > 0:
                    if not alert.notified:
                        # send notification
                        self.notify_about_alert(alert)
                        alert.notified = True
            alerts_to_update[alert_id] = alert
        for alert_id in alerts_to_update:
            self.alert_cache[alert_id] = alerts_to_update[alert_id]

    def notify_about_alert(self, alert):
        print "totally notifying about {0}".format(alert.id.split("?x=")[1])


if __name__ == '__main__':
    fetcher = AlertFetcher()
    fetcher.fetch_feed()
    fetcher.scheduler.add_job(fetcher.fetch_feed, 'interval', minutes=2)
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        fetcher.scheduler.shutdown()
