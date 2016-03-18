#!/usr/bin/python
# =======================================
#
#  File Name : slackbot_settings.py
#
#  Purpose :
#
#  Creation Date : 18-03-2016
#
#  Last Modified : Fri 18 Mar 2016 12:02:44 PM CDT
#
#  Created By : Brian Auron
#
# ========================================

import yaml
with open('config.yml', 'r') as yml:
    config = yaml.load(yml.read())

API_TOKEN = config['API_TOKEN']

PLUGINS = [
        'slackbutt',
        ]
