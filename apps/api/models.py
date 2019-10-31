from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class AdminProfile(models.Model):
	user=models.OneToOneField(User,on_delete=models.CASCADE)
	mobile_number=models.CharField(null=True,blank=True,max_length=100)
