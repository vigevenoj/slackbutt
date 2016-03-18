#!/usr/bin/python
# =======================================
#
#  File Name : plugins.py
#
#  Purpose :
#
#  Creation Date : 18-03-2016
#
#  Last Modified : Fri 18 Mar 2016 12:19:54 PM CDT
#
#  Created By : Brian Auron
#
# ========================================

import slackbot.bot
import re

SHENANISTRING = '''what's the name of that place you like with all the goofy\
 shit on the walls?'''
SHENANIGANS = [SHENANISTRING, re.IGNORECASE]
@slackbot.bot.respond_to(*SHENANIGANS)
def shenanigans(message):
    message.reply('You mean Shenanigans? You guys talkin\' \'bout\
 shenanigans?')

HI = re.compile(r'hi(|!)$', re.IGNORECASE)
@slackbot.bot.respond_to(HI)
def hi(message, groups):
    message.reply('Yo!')

TOWELSTRING = '''you're a towel'''
TOWEL = re.compile(TOWELSTRING, re.IGNORECASE)
@slackbot.bot.listen_to(TOWEL)
def towel(message):
    message.reply('''YOU'RE a towel!''')

PYTHONTOWELSTRING = '''you're a (bot|python|robot) towel'''
PYTHONTOWEL = re.compile(PYTHONTOWELSTRING, re.IGNORECASE)
@slackbot.bot.listen_to(PYTHONTOWEL)
def towel(message):
    message.reply('''What did you say?!''')
