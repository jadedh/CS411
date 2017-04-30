# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models

class QueryText(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    query = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = 'query_text'

class QueryData(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    query = models.ForeignKey(QueryText, models.DO_NOTHING)
    lat = models.FloatField()
    long = models.FloatField()

    class Meta:
        managed = False
        db_table = 'query_data'

class JsonCache(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    userid = models.IntegerField(unique=True)
    json = models.TextField()
    timestamp = models.TextField()

    class Meta:
        managed = False
        db_table = 'json_cache'

class UserData(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    userid = models.IntegerField(unique=True)
    loc = models.TextField()
    dist = models.TextField()
    tag = models.TextField()
    lim = models.TextField()

    class Meta:
        managed = False
        db_table = 'user_data'




