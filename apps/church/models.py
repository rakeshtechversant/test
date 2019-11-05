from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime
# Create your models here.
from django.utils import timezone


class Notice(models.Model):
    notice = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=10000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    image = models.ImageField(upload_to='members/', null=True, blank=True)


class FileUpload(models.Model):
    primary_user_id = models.AutoField(max_length=5, primary_key=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to='members/', null=True, blank=True)
    address = models.TextField(max_length=500, null=True, blank=True)
    phone_no_primary = models.CharField(max_length=20, null=True, blank=True)
    phone_no_secondary = models.CharField(max_length=20, null=True, blank=True)
    dob = models.CharField(max_length=20, null=True, blank=True)
    dom = models.CharField(max_length=20, null=True, blank=True)
    blood_group = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    occupation = models.CharField(max_length=200)
    about = models.TextField(max_length=1000, null=True, blank=True)
    marital_status = models.CharField(max_length=20,null=True,blank=True)
    in_memory = models.BooleanField(default=False)
    in_memory_date = models.CharField(max_length=20, null=True, blank=True)


    def __str__(self):
        return self.name


class Family(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    about = models.TextField(max_length=500, null=True, blank=True)
    members_length = models.IntegerField(default=0)
    primary_user_id = models.ForeignKey(FileUpload, on_delete=models.CASCADE, related_name='get_file_upload', null=True,
                                        blank=True)

    def __str__(self):
        return self.name


class Members(models.Model):
    secondary_user_id = models.AutoField(max_length=5, primary_key=True)
    member_name = models.CharField(max_length=255, null=True, blank=True)
    relation = models.CharField(max_length=255, null=True, blank=True)
    dob = models.CharField(max_length=20, null=True, blank=True)
    dom = models.CharField(max_length=20, null=True, blank=True)
    image = models.ImageField(upload_to='members/', null=True, blank=True)
    phone_no_secondary_user = models.CharField(max_length=20, null=True, blank=True)
    phone_no_secondary_user_secondary = models.CharField(max_length=20, null=True, blank=True)
    primary_user_id = models.ForeignKey(FileUpload, on_delete=models.CASCADE, related_name='get_primary_user',
                                        null=True, blank=True)
    blood_group = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    occupation = models.CharField(max_length=200, null=True, blank=True)
    about = models.TextField(max_length=1000, null=True, blank=True)
    marital_status = models.CharField(max_length=20,null=True,blank=True)
    in_memory = models.BooleanField(default=False)
    in_memory_date = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.member_name


class UnapprovedMember(models.Model):
    """hold details of unapproved members until admin approve
    """
    secondary_user_id = models.AutoField(max_length=5, primary_key=True)
    member_name = models.CharField(max_length=255, null=True, blank=True)
    relation = models.CharField(max_length=255, null=True, blank=True)
    dob = models.CharField(max_length=20, null=True, blank=True)
    dom = models.CharField(max_length=20, null=True, blank=True)
    image = models.ImageField(upload_to='members/', null=True, blank=True)
    phone_no_secondary_user = models.CharField(max_length=20, null=True, blank=True)
    phone_no_secondary_user_secondary = models.CharField(max_length=20, null=True, blank=True)
    primary_user_id = models.ForeignKey(FileUpload, on_delete=models.CASCADE, null=True, blank=True)
    blood_group = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    occupation = models.CharField(max_length=200, null=True, blank=True)
    about = models.TextField(max_length=1000, null=True, blank=True)
    marital_status = models.CharField(max_length=20,null=True,blank=True)
    in_memory = models.BooleanField(default=False)
    in_memory_date = models.CharField(max_length=20, null=True, blank=True)
    rejected = models.BooleanField(default=False)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True, blank=True)
    dob = models.DateField(null=True, blank=True, default=timezone.now)
    address = models.TextField(max_length=500)
    occupation = models.CharField(max_length=200, null=True, blank=True)
    about = models.TextField(max_length=5000)
    profile_image = models.FileField(upload_to='cards/pan_folder/', null=True, blank=True)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    date_of_marriage = models.DateTimeField(null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    is_otp_verified = models.BooleanField(default=False)
    # secondary_user = models.ManyToManyField(Members)
    is_church_user = models.BooleanField(default=False)


class PrayerGroup(models.Model):
    # user_profile = models.ManyToManyField(FileUpload)
    primary_user_id = models.ForeignKey(FileUpload, on_delete=models.CASCADE,
                                        related_name='get_file_upload_prayergroup', null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, null=True, blank=True)


class Images(models.Model):
    image = models.FileField(upload_to='pan_folder/')
    title = models.CharField(max_length=200)
    date = models.DateField(default=timezone.now)


class ChurchDetails(models.Model):
    church_name = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(max_length=5000, null=True, blank=True)
    image = models.ManyToManyField(Images)
    cover_image = models.FileField(upload_to='pan_folder/', null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    vicar_inf = models.TextField(max_length=1000, null=True, blank=True)
    vicar_image=models.FileField(upload_to='pan_folder/', null=True, blank=True)
    vicar_name=models.CharField(max_length=100,null=True,blank=True)

    class Meta:
        verbose_name_plural = "ChurchDetails"


PRIMARY = 'PRIMARY'
SECONDARY = 'SECONDARY'
CHURCH = 'CHURCH'

USER_TYPE = (
    (PRIMARY, 'PRIMARY'),
    (SECONDARY, 'SECONDARY'),
    (CHURCH, 'CHURCH'),
)


class OtpModels(models.Model):
    mobile_number = models.CharField(max_length=20)
    user_type = models.CharField(max_length=255, choices=USER_TYPE, null=True, blank=True)
    otp = models.CharField(max_length=20)
    created_time = models.DateTimeField(default=datetime.now, blank=True)
    is_expired = models.BooleanField(default=False)


class OtpVerify(models.Model):
    otp = models.CharField(max_length=20)


class Notification(models.Model):
    user = models.ForeignKey(FileUpload, on_delete=models.CASCADE, null=True, blank=True)
    is_new_register = models.BooleanField(default=False)
    is_user_add_new_member = models.BooleanField(default=False)
    created_time = models.DateTimeField(default=timezone.now, blank=True)


class NoticeBereavement(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(max_length=100, null=True, blank=True)
    prayer_group = models.ForeignKey(PrayerGroup, on_delete=models.CASCADE, null=True, blank=True)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True, blank=True)
    primary_member = models.ForeignKey(FileUpload, on_delete=models.CASCADE, null=True, blank=True)
    secondary_member = models.ForeignKey(Members, on_delete=models.CASCADE, null=True, blank=True)
