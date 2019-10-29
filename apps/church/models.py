from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime
# Create your models here.
from django.utils import timezone

class Notice(models.Model):
	notice = models.CharField(max_length=255,null=True,blank=True)
	image = models.FileField(upload_to = 'cards/pan_folder/',null=True,blank=True)




class Family(models.Model):
	name = models.CharField(max_length = 255,null=True,blank=True)
	members_length = models.IntegerField(default=0)


class FileUpload(models.Model):
	user = models.CharField(max_length = 200,null=True,blank=True)
	first_name = models.CharField(max_length = 200,null=True,blank=True)
	last_name = models.CharField(max_length = 200,null=True,blank=True)
	dob= models.DateField(null=True, blank=True, default=timezone.now)
	date_of_marriage = models.DateField(null=True,blank=True)
	address=models.TextField(max_length=500)
	occupation = models.CharField(max_length=200)
	about = models.TextField(max_length=5000)
	profile_image = models.FileField(upload_to = 'cards/pan_folder/',null=True,blank=True)
	mobile_number = models.CharField(max_length = 20,null=True,blank=True)



class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
	family = models.ForeignKey(Family,on_delete=models.CASCADE,null=True,blank = True)
	dob= models.DateField(null=True, blank=True, default=timezone.now)
	address=models.TextField(max_length=500)
	occupation = models.CharField(max_length=200)
	about = models.TextField(max_length=5000)
	profile_image = models.FileField(upload_to = 'cards/pan_folder/',null=True,blank=True)
	mobile_number = models.CharField(max_length = 20,null=True,blank=True)
	date_of_marriage = models.DateTimeField(null=True,blank=True)
	is_primary = models.BooleanField(default=False)
	is_otp_verified = models.BooleanField(default=False)
	secondary_user = models.ManyToManyField(FileUpload)
	is_church_user = models.BooleanField(default=False)





class PrayerGroup(models.Model):
	user_profile = models.ManyToManyField(FileUpload)
	name = models.CharField(max_length=255,null=True,blank=True)
	notice = models.ForeignKey(Notice,on_delete=models.CASCADE,null=True,blank=True)

class Images(models.Model):
	image = models.FileField(upload_to = 'cards/pan_folder/',null=True,blank=True)

class ChurchDetails(models.Model):
	church_name = models.CharField(max_length = 200,null=True,blank=True)
	description = models.TextField(max_length=5000,null=True,blank=True)
	image = models.ManyToManyField(Images)
	cover_image = models.FileField(upload_to = 'cards/pan_folder/',null=True,blank=True)
	address = models.CharField(max_length=200,null=True,blank=True)

	class Meta:
		verbose_name_plural = "ChurchDetails"

PRIMARY='PRIMARY'
SECONDARY='SECONDARY'
CHURCH='CHURCH'

USER_TYPE = (
    (PRIMARY, 'PRIMARY'),
    (SECONDARY, 'SECONDARY'),
    (CHURCH, 'CHURCH'),
)


class OtpModels(models.Model):
	mobile_number = models.CharField(max_length = 20)
	user_type = models.CharField(max_length=255, choices=USER_TYPE, null=True, blank=True)
	otp = models.CharField(max_length = 20)
	created_time = models.DateTimeField(default=datetime.now, blank=True)
	is_expired = models.BooleanField(default=False)

class OtpVerify(models.Model):
	otp = models.CharField(max_length = 20)


class Notification(models.Model):
	user = models.ForeignKey(UserProfile,on_delete=models.CASCADE,null=True,blank=True)
	is_new_register = models.BooleanField(default = False)
	is_user_add_new_member = models.BooleanField(default = False)
	created_time = models.DateTimeField(default=timezone.now, blank=True)
