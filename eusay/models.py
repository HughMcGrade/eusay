'''
Created on 18 Feb 2014

@author: Hugh
'''
from django.db import models

class Comment (models.Model):
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=500)
    user = models.ForeignKey() #TODO
    proposal = models.ForeignKey()
    date = models.DateField()
    
class User (models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    
    