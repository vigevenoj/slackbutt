#!/usr/bin/python
# =======================================
#
#  File Name : runbot.py
#
#  Purpose :
#
#  Creation Date : 18-03-2016
#
#  Last Modified : Fri 18 Mar 2016 11:35:24 AM CDT
#
#  Created By : Brian Auron
#
# ========================================

import slackbot.bot

def main():
    bot = slackbot.bot.Bot()
    bot.run()

if __name__ == '__main__':
    main()
