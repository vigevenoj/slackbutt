
import re
import slackbot.bot
import requests
from datetime import datetime, timedelta

URL = 'http://api.open-notify.org/iss-pass.json?lat={0}&lon={1}'
LONGITUDE = -122.680372
LATITUDE = 45.522005


class SpaceStation():
    def __init__(self, longitude=-122.680372, latitude=45.522005):
        if (latitude is None):
            self._latitude = 45.522005
        else:
            self._latitude = latitude
        if (longitude is None):
            self._longitude = -122.680372
        else:
            self._longitude = longitude

    @property
    def longitude(self):
        return self._longitude

    @property
    def latitude(self):
        return self._latitude

    @longitude.setter
    def longitude(self, longitude):
        self._longitude = longitude

    @latitude.setter
    def latitude(self, latitude):
        self._latitude = latitude

    def next_pass(self):
        reply = "nobody knows anything about a space station"
        url = URL.format(self._latitude, self._longitude)
        data = requests.get(url)
        if data.status_code == 200:
            api_response = data.json()
            if (api_response['message'] == 'success'):
                next_rise_time = api_response['response'][0]['risetime']
                next_duration = api_response['response'][0]['duration']
                dt = datetime.fromtimestamp(next_rise_time)
                done = dt + timedelta(seconds=next_duration)
                reply = "Next pass from {0} until {1}".format(
                    dt, done)
            else:
                print "had problem with api not success"

        else:
            print "status code was {0}".format(data.status_code)
        return reply

ISS_STRING = r'''iss\s?((-?[\d]+\.[\d]+)[,]?\s(-?[\d]+\.[\d]+))?'''
ISS = re.compile(ISS_STRING, re.IGNORECASE)


@slackbot.bot.respond_to(ISS)
def do_iss(message, *groups):
    print "someone asked about the international space station!"
    try:
        longitude, latitude = groups[1], groups[2]
    except IndexError:
        longitude, latitude = LONGITUDE, LATITUDE  # constants for pdx
    iss = SpaceStation(longitude, latitude)
    msg = iss.next_pass()
    message.reply(msg)


if __name__ == '__main__':
    iss = SpaceStation(LONGITUDE, LATITUDE)
    print iss.next_pass()
