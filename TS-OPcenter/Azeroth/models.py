from django.db import models
from django.contrib.auth.models import User
# Create your models here.
import datetime



class UserToken(models.Model):
    user = models.OneToOneField(User)
    token = models.CharField(max_length=128,verbose_name='用户token')
    update_time = models.DateTimeField(default=datetime.datetime.now,verbose_name='添加时间')