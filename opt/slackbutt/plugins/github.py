#!/usr/bin/python
# =======================================
#
#  File Name : github.py
#
#  Purpose :
#
#  Creation Date : 27-03-2016
#
#  Last Modified : Sun 27 Mar 2016 09:14:18 AM CDT
#
#  Created By : Brian Auron
#
# ========================================

import requests
import yaml
import json
import re
import slackbot.bot

with open('config.yml', 'r') as yml:
    cfg = yaml.load(yml.read())

URL = cfg['github']['url']
OWNER = cfg['github']['owner']
REPO = cfg['github']['repo']
TOKEN = cfg['github']['token']
HEADERS = {'Content-Type': 'application/json',
           'Authorization': 'token %s' % TOKEN}

class Issue(object):
    def __init__(self):
        self.uri = URL+'/repos/%s/%s/issues' % (OWNER, REPO)
    def list(self, params={}):
        req = requests.get(self.uri, headers=HEADERS, params=params)
        return json.loads(req.text)
    def create(self, title, body):
        data = {'title': title, 'body': body}
        req = requests.post(self.uri, headers=HEADERS, data=json.dumps(data))
        return json.loads(req.text)


LISTISSUESTRING = r'''github\slist\sissues?
                      ($|\sopen|\sclosed)'''
LISTISSUES = re.compile(LISTISSUESTRING, re.IGNORECASE|re.VERBOSE)
@slackbot.bot.respond_to(LISTISSUES)
def list_issues(message, *groups):
    param = groups[0]
    params = {}
    if param:
        params['state'] = param
    resp = Issue().list(params=params)
    if len(resp) == 0:
        message.reply('0 issues found.')
        return
    [message.reply(i['html_url']) for i in resp]
    #print 'Got a message %s with groups "%s"' % (message.body, groups)

CREATEISSUESTRING = r'''github\screate\sissue\s
                        ((title\s)?(".*"))\s
                        ((body\s)?(".*"))$'''
CREATEISSUE = re.compile(CREATEISSUESTRING, re.IGNORECASE|re.VERBOSE)
@slackbot.bot.respond_to(CREATEISSUE)
def create_issue(message, *groups):
    title = groups[2].strip('"')
    body = groups[5].strip('"')
    resp = Issue().create(title, body)
    message.reply(resp['html_url'])
    #print 'Got a message %s with groups "%s"' % (message.body, groups)
