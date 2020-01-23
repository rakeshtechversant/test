from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime
# Create your models here.
from django.utils import timezone

from apps.api.models import AdminProfile
from ckeditor.fields import RichTextField


class Notice(models.Model):
    notice = models.CharField(max_length=255)
    description = models.TextField(max_length=10000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    image = models.FileField(upload_to='pan_folder/', null=True, blank=True)


class FileUpload(models.Model):
    primary_user_id = models.AutoField(max_length=5, primary_key=True)
    name = models.CharField(max_length=200)
    image = models.FileField(upload_to='members/', null=True, blank=True)
    address = models.TextField(max_length=500, null=True, blank=True)
    phone_no_primary = models.CharField(max_length=20, null=True, blank=True)
    phone_no_secondary = models.CharField(max_length=20, null=True, blank=True)
    dob = models.CharField(max_length=20, null=True, blank=True)
    dom = models.CharField(max_length=20, null=True, blank=True)
    blood_group = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    occupation = models.CharField(max_length=200, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    marital_status = models.CharField(max_length=20,null=True,blank=True)
    marrige_date = models.CharField(max_length=20,null=True,blank=True)
    in_memory = models.BooleanField(default=False)
    in_memory_date =models.DateTimeField(null=True, blank=True)
    relation = models.CharField(max_length=255, null=True, blank=True)


    def __str__(self):
        return self.name


class Family(models.Model):
    name = models.CharField(max_length=255)
    about = models.TextField(null=True, blank=True)
    image = models.FileField(upload_to='familyimage/', null=True, blank=True)
    members_length = models.IntegerField(default=0)
    primary_user_id = models.ForeignKey(FileUpload, on_delete=models.CASCADE, related_name='get_file_upload', null=True,
                                        blank=True)

    def __str__(self):
        return self.name


class Members(models.Model):
    secondary_user_id = models.AutoField(max_length=5, primary_key=True)
    member_name = models.CharField(max_length=255)
    relation = models.CharField(max_length=255, null=True, blank=True)
    dob = models.CharField(max_length=20, null=True, blank=True)
    dom = models.CharField(max_length=20, null=True, blank=True)
    image = models.FileField(upload_to='members/', null=True, blank=True)
    phone_no_secondary_user = models.CharField(max_length=20, null=True, blank=True)
    phone_no_secondary_user_secondary = models.CharField(max_length=20, null=True, blank=True)
    primary_user_id = models.ForeignKey(FileUpload, on_delete=models.CASCADE, related_name='get_primary_user',
                                        null=True, blank=True)
    blood_group = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    occupation = models.CharField(max_length=200, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    marital_status = models.CharField(max_length=20,null=True,blank=True)
    marrige_date = models.CharField(max_length=20,null=True,blank=True)
    in_memory = models.BooleanField(default=False)
    in_memory_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.member_name


class UnapprovedMember(models.Model):
    """hold details of unapproved members until admin approve
    """
    secondary_user_id = models.AutoField(max_length=5, primary_key=True)
    member_name = models.CharField(max_length=255)
    relation = models.CharField(max_length=255, null=True, blank=True)
    dob = models.CharField(max_length=20, null=True, blank=True)
    dom = models.CharField(max_length=20, null=True, blank=True)
    image = models.FileField(upload_to='members/', null=True, blank=True)
    phone_no_secondary_user = models.CharField(max_length=20, null=True, blank=True)
    phone_no_secondary_user_secondary = models.CharField(max_length=20, null=True, blank=True)
    primary_user_id = models.ForeignKey(FileUpload, on_delete=models.CASCADE, null=True, blank=True)
    blood_group = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    occupation = models.CharField(max_length=200, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    marital_status = models.CharField(max_length=20,null=True,blank=True)
    marrige_date = models.CharField(max_length=20,null=True,blank=True)
    in_memory = models.BooleanField(default=False)
    in_memory_date = models.DateTimeField(null=True, blank=True)
    rejected = models.BooleanField(default=False)
    edit_user = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=200, null=True, blank=True)
    date=models.DateTimeField(default=datetime.now, blank=True)
    
    def __str__(self):
        return self.member_name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True, blank=True)
    dob = models.DateField(null=True, blank=True, default=timezone.now)
    address = models.TextField(max_length=500)
    occupation = models.CharField(max_length=200, null=True, blank=True)
    about = models.TextField(null=True,blank=True)
    profile_image = models.FileField(upload_to='pan_folder/', null=True, blank=True)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    date_of_marriage = models.DateTimeField(null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    is_otp_verified = models.BooleanField(default=False)
    # secondary_user = models.ManyToManyField(Members)
    is_church_user = models.BooleanField(default=False)


class Notice(models.Model):
    notice = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=10000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    image = models.FileField(upload_to='pan_folder/', null=True, blank=True)


class PrayerGroup(models.Model):
    # user_profile = models.ManyToManyField(FileUpload)
    family = models.ManyToManyField(Family, null=True, blank=True)
    primary_user_id = models.ManyToManyField(FileUpload,
                    related_name='get_file_upload_prayergroup', null=True, blank=True)
    sec_member = models.ManyToManyField(Members,null=True,blank=True)
    name = models.CharField(max_length=255)
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class Images(models.Model):
    image = models.FileField(upload_to='pan_folder/')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    date = models.DateField(default=timezone.now)

class ChurchDetails(models.Model):
    church_name = models.CharField(max_length=200)
    description = models.TextField(max_length=5000, null=True, blank=True)
    image = models.ManyToManyField(Images)
    cover_image = models.FileField(upload_to='pan_folder/', null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    vicar_inf = models.TextField(max_length=50000, null=True, blank=True)
    vicar_image=models.FileField(upload_to='pan_folder/', null=True, blank=True)
    vicar_name=models.CharField(max_length=100,null=True,blank=True)

    class Meta:
        verbose_name_plural = "ChurchDetails"


class ChurchVikar(models.Model):
    church = models.ForeignKey(ChurchDetails, on_delete=models.CASCADE)
    vicar_name = models.CharField(max_length=100)
    vicar_info = models.TextField(max_length=1000, null=True, blank=True)
    vicar_image = models.FileField(upload_to='pan_folder/', null=True, blank=True)


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
    created_by_admin = models.ForeignKey(AdminProfile, on_delete=models.CASCADE, null=True, blank=True,related_name='created_by_admin')
    created_by_primary = models.ForeignKey(FileUpload, on_delete=models.CASCADE, null=True, blank=True,related_name='created_by_primary')
    created_by_secondary = models.ForeignKey(Members, on_delete=models.CASCADE, null=True, blank=True,related_name='created_by_secondary')
    # is_new_register = models.BooleanField(default=False)
    # is_user_add_new_member = models.BooleanField(default=False)
    created_time = models.DateTimeField(default=timezone.now, null=True, blank=True)
    message=models.TextField(max_length=1000)
    notification_to_primary = models.ManyToManyField(FileUpload, through='NoticeReadPrimary')
    notification_to_secondary = models.ManyToManyField(Members, through='NoticeReadSecondary')
    notification_to_admin = models.ManyToManyField(AdminProfile, through='NoticeReadAdmin')
    is_json=models.BooleanField(default=False)

class NoticeReadPrimary(models.Model):
    notification=models.ForeignKey(Notification, on_delete=models.CASCADE, null=True, blank=True)
    user_to=models.ForeignKey(FileUpload, on_delete=models.CASCADE, null=True, blank=True)
    is_read=models.BooleanField(default=False)

class NoticeReadSecondary(models.Model):
    notification=models.ForeignKey(Notification, on_delete=models.CASCADE, null=True, blank=True)
    user_to=models.ForeignKey(Members, on_delete=models.CASCADE, null=True, blank=True)
    is_read=models.BooleanField(default=False)

class NoticeReadAdmin(models.Model):
    notification=models.ForeignKey(Notification, on_delete=models.CASCADE, null=True, blank=True)
    user_to=models.ForeignKey(AdminProfile, on_delete=models.CASCADE, null=True, blank=True)
    is_read=models.BooleanField(default=False)

class NoticeBereavement(models.Model):
    # title = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    description = models.TextField(max_length=100, null=True, blank=True)
    prayer_group = models.ForeignKey(PrayerGroup, on_delete=models.CASCADE, null=True, blank=True)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True, blank=True)
    primary_member = models.ForeignKey(FileUpload, on_delete=models.CASCADE, null=True, blank=True)
    secondary_member = models.ForeignKey(Members, on_delete=models.CASCADE, null=True, blank=True)


class ViewRequestNumber(models.Model):
    request_from = models.CharField(max_length=200, null=True, blank=True)
    usertype_from = models.CharField(max_length=200, null=True, blank=True)
    request_to = models.CharField(max_length=200, null=True, blank=True)
    usertype_to = models.CharField(max_length=200, null=True, blank=True)
    request_mobile = models.CharField(max_length=12, null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    date=models.DateTimeField(default=datetime.now, blank=True)


class Occupation(models.Model):
    occupation = models.CharField(max_length=200, unique=True)

class MemberType(models.Model):
    member_type =  models.CharField(max_length=200, unique=True)


class PrivacyPolicy(models.Model):
    policy=RichTextField(null=True,blank=True)


IOS = 'IOS'
ANDROID = 'ANDROID'


PHONE_TYPE = (
    (IOS, 'IOS'),
    (ANDROID, 'ANDROID'),
)

class PhoneVersion(models.Model):
    version = models.CharField(max_length=20)
    phone_type = models.CharField(max_length=255, choices=PHONE_TYPE, null=True, blank=True)

class ChurchFolder(models.Model):
    church_img = models.ForeignKey(Images, related_name="churchfolder", on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    parent = models.ForeignKey("self", null=True, on_delete=models.CASCADE, blank=True)

    @property
    def get_folder_path(self):
        if self.parent:
            return self.parent.get_folder_path + "/" + self.name
        return ""

class Meta:
    unique_together = ("church_img", "name", "parent")


class PrimaryToSecondary(models.Model):
    request_from = models.CharField(max_length=200, null=True, blank=True)
    usertype_from = models.CharField(max_length=200, null=True, blank=True)
    request_to = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=200, null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    date=models.DateTimeField(default=datetime.now, blank=True)

class NumberChangePrimary(models.Model):
    request_from_primary = models.CharField(max_length=200, null=True, blank=True)
    number_from = models.CharField(max_length=12, null=True, blank=True)
    number_to = models.CharField(max_length=12, null=True, blank=True)
    status = models.CharField(max_length=200, null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    date=models.DateTimeField(default=datetime.now, blank=True)