from django.db import models

# Create your models here.
class xml(models.Model):
	path = models.CharField(max_length=255)
	description = models.CharField(max_length=1024)
	status = models.CharField(max_length=16)
	
class machines(models.Model):
	ip = models.CharField(max_length=16, primary_key=True)
	macid = models.IntegerField()
	totalcount = models.IntegerField()
	countnow = models.IntegerField()
	projectid = models.IntegerField()
	status = models.CharField(max_length=16)
	lastback = models.BigIntegerField()
	lastmodify = models.BigIntegerField()

class projects(models.Model):
	name = models.CharField(max_length=255)
	description = models.CharField(max_length = 1024)
	xmlid = models.IntegerField()
	totalmachines = models.IntegerField()
	allocindex = models.IntegerField()
	status = models.CharField(max_length = 16)


class logs(models.Model):
	ip = models.CharField(max_length=16)
	projectid = models.IntegerField()
	macid = models.IntegerField()
	path = models.CharField(max_length=255)
	time = models.BigIntegerField()

class crashs(models.Model):
	ip = models.CharField(max_length=16)
	projectid = models.IntegerField()
	macid = models.IntegerField()
	countnow = models.IntegerField()
	status = models.CharField(max_length = 16)#handled or not
#project:{id(pkey), name, description, xmlid, totalmachines,allocindex ,status[deleted, stop, over, running]}














#machines:{ip(pkey), id, totalcount, countnow, projectid, status[inuse, free, death, pdeath]}
