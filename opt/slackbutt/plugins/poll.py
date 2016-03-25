#!/usr/bin/python
# =======================================
#
#  File Name : poll.py
#
#  Purpose :
#
#  Creation Date : 18-03-2016
#
#  Last Modified : Fri 25 Mar 2016 12:22:56 PM CDT
#
#  Created By : Brian Auron
#
# ========================================

import peewee
import playhouse.postgres_ext as pe
import yaml
import re
import functools

YAML = 'config.yml'
with open(YAML, 'r') as yml:
    cfg = yaml.load(yml.read())
dbuser = cfg['dbuser']
dbpass = cfg['dbpass']
db = cfg['db']
psql_db = pe.PostgresqlExtDatabase(db, user=dbuser, password=dbpass)

def connect(func):
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    try:
      psql_db.connect()
      return func(*args, **kwargs)
    finally:
      psql_db.close()
  return wrapper

class Poll(peewee.Model):
    title = peewee.TextField()
    opened = peewee.DateTimeField()
    close = peewee.DateTimeField()
    closed = peewee.BooleanField(default=False)

class Option(peewee.Model):
    name = peewee.TextField()
    poll = peewee.ForeignKeyField(Poll, related_name='related_poll')

    class Meta:
        database = psql_db

class User(peewee.Model):
    name = peewee.CharField(unique = True)

    class Meta:
        database = psql_db

class User2Option(peewee.Model):
    option = peewee.ForeignKeyField(Option)
    user = peewee.ForeignKeyField(User)
    vote = peewee.IntegerField(constraints = [peewee.Check('vote = 1')])
    class Meta:
        indexes = (
            (('option', 'user'), True),
        )
        database = psql_db

def create_ratings():
    psql_db.connect()
    psql_db.create_tables([Poll, Option, User, User2Option])

def drop_ratings():
    psql_db.connect()
    psql_db.drop_tables([Poll, Option, User, User2Option])

@connect
def poll_results(poll_id):
    # TODO: get poll results by id or something
    pass
