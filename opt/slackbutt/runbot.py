#!/usr/bin/python
# =======================================
#
#  File Name : runbot.py
#
#  Purpose :
#
#  Creation Date : 18-03-2016
#
#  Last Modified : Fri 25 Mar 2016 05:54:59 PM CDT
#
#  Created By : Brian Auron
#
# ========================================

import slackbot.bot
import logging

CONFIG = 'config.yml'

def main():
    logging.basicConfig()
    LOGGER = logging.getLogger('slackbot')
    bot = slackbot.bot.Bot()
    bot.run()

if __name__ == '__main__':
    main()
