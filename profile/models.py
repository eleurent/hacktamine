#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from probleme.models import Probleme

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length = 128)
    last_name = models.CharField(max_length = 255)
    team = models.CharField(max_length = 128)
    
    def __unicode__(self):
        return self.first_name + " " + self.last_name
        
    def probleme(self):
        problemes = Probleme.objects.exclude(id__in = self.user.probleme_set.all())
        if problemes:
            return problemes[0]
        else:
            return None 