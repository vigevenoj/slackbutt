
import re
import slackbot.bot
import requests
from datetime import datetime, timedelta

URL = 'http://api.open-notify.org/iss-pass.json?lat={0}&lon={1}'


class SpaceStation():
    def __init__(self):
        self._latitude = 45.522005
        self._longitude = 45.522005

#    @property
#    def location(self):
#        return (self._longitude, self._latitude)

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

ISS_STRING = r'''iss'''
ISS = re.compile(ISS_STRING, re.IGNORECASE)


@slackbot.bot.respond_to(ISS)
def do_iss(message, *groups):
    print "someone asked about the international space station!"
    iss = SpaceStation()
    msg = iss.next_pass()
    message.reply(msg)


if __name__ == '__main__':
    iss = SpaceStation()
    iss.next_pass()
