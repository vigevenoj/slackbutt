#!/usr/bin/python
# =======================================
#
#  File Name : slackbot_settings.py
#
#  Purpose :
#
#  Creation Date : 18-03-2016
#
#  Last Modified : Mon 21 Mar 2016 12:39:37 PM CDT
#
#  Created By : Brian Auron
#
# ========================================

import yaml
from runbot import CONFIG
with open(CONFIG, 'r') as yml:
    config = yaml.load(yml.read())

API_TOKEN = config['API_TOKEN']

PLUGINS = [
        'plugins',
        ]
