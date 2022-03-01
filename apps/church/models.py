from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime
# Create your models here.
from django.utils import timezone

from apps.api.models import AdminProfile
from ckeditor.fields import RichTextField
from django.utils import timezone as tz
from push_notifications.models import APNSDevice, GCMDevice
from django.conf import settings
import asyncio

STATUS_CHOICES = (
    ("1", "Active"),
    ("2", "InActive"),
    ("3", "Not in Oman"),
    ("4", "Ex-Parish Member"),
)


def mongo_archive_decorator(archive_func):
    def wrapped(*args, **kwargs):
        asyncio.set_event_loop(asyncio.new_event_loop())
        return asyncio.get_event_loop().run_in_executor(None, archive_func, *args, *kwargs)
    return wrapped


@mongo_archive_decorator
def notifications_for_notice(self):
    body = "You have received a new notice"
    notifications = Notification.objects.create(created_time=tz.now(), message=body)
    primary_members = FileUpload.objects.all()
    secondary_members = Members.objects.all()
    for primary_member in primary_members:
        NoticeReadPrimary.objects.create(notification=notifications, user_to=primary_member, is_read=False)
    for secondary_member in secondary_members:
        NoticeReadSecondary.objects.create(notification=notifications, user_to=secondary_member, is_read=False)
    try:
        if self.image == None and self.video == None and self.audio != None:
            image = "https://cdn0.iconfinder.com/data/icons/cosmo-documents/40/file_audio-512.png"
        elif self.image == None and self.audio == None and self.video != None:
            image = settings.DEFAULT_DOMAIN + str(self.thumbnail.url)
        else:
            image = settings.DEFAULT_DOMAIN + str(self.image.url)
    except:
        image = ""
    try:
        content = {'title': 'notice title',
                   'message':
                       {"data":
                            {"title": "Notice",
                             "body": str(self.notice),
                             "notificationType": "notice",
                             "backgroundImage": image,
                             "image": image,
                             "text_type": "short"},
                        "notification":
                            {"alert": "This is a FCM notification",
                             "title": "Notice",
                             "body": str(self.notice),
                             "sound": "default",
                             "backgroundImage": image,
                             "backgroundImageTextColour": "#FFFFFF",
                             "image": image,
                             "click_action": "notice"
                             }
                        }
                   }
        content_ios = {'message':
                           {"aps":
                                {"alert":
                                     {"title": "Notice",
                                      "subtitle": "",
                                      "body": str(self.notice)
                                      },
                                 "sound": "default",
                                 "category": "notice",
                                 "badge": 1,
                                 "mutable-content": 1
                                 },
                            "media-url": image
                            }
                       }
        fcm_messaging_to_all(content)
        apns_messaging_to_all(content_ios)
    except:
        pass


@mongo_archive_decorator
def notifications_for_notice_bereavement_create(self):
    try:
        name, family_name, image = '', '', ''
        if self.family:
            family_name = self.family.name
            if self.primary_member:
                name = self.primary_member.name
                try:
                    image = settings.DEFAULT_DOMAIN + str(self.primary_member.image.url)
                except:
                    pass
            elif self.secondary_member:
                name = self.secondary_member.member_name
                try:
                    image = settings.DEFAULT_DOMAIN + str(self.secondary_member.image.url)
                except:
                    pass
        else:
            if self.primary_member:
                name = self.primary_member.name
                family_name = self.primary_member.get_file_upload.first().name
                try:
                    image = settings.DEFAULT_DOMAIN + str(self.primary_member.image.url)
                except:
                    pass
            elif self.secondary_member:
                name = self.secondary_member.member_name
                family_name = self.secondary_member.primary_user_id.get_file_upload.first().name
                try:
                    image = settings.DEFAULT_DOMAIN + str(self.secondary_member.image.url)
                except:
                    pass

        if family_name:
            body = {"message": "Funeral announcement of %s belonging to %s" % (name, family_name),
                    "user_type": "SECONDARY",
                    "type": "bereavement",
                    "id": str(self.id)
                    }
        else:
            body = {"message": "Funeral announcement of %s" % name,
                    "user_type": "SECONDARY",
                    "type": "bereavement",
                    "id": str(self.id)
                    }
        notifications = Notification.objects.create(created_time=tz.now(), message=body)
        primary_members = FileUpload.objects.all()
        secondary_members = Members.objects.all()
        for primary_member in primary_members:
            NoticeReadPrimary.objects.create(notification=notifications, user_to=primary_member, is_read=False)
        for secondary_member in secondary_members:
            NoticeReadSecondary.objects.create(notification=notifications, user_to=secondary_member, is_read=False)
        try:
            content = {'title': 'notice title',
                       'message':
                           {
                               "data":
                                   {
                                       "title": "Funeral Notice",
                                       "body": "Funeral announcement of %s belonging to %s" % (name, family_name),
                                       "notificationType": "funeral",
                                       "backgroundImage": image,
                                       "text_type": "long"
                                   },
                               "notification":
                                   {"alert": "This is a FCM notification",
                                    "title": "Funeral Notice",
                                    "body": "Funeral announcement of %s belonging to %s" % (name, family_name),
                                    "sound": "default",
                                    "backgroundImage": image,
                                    "backgroundImageTextColour": "#FFFFFF",
                                    "image": image,
                                    "click_action": "notice"
                                    }
                           }
                       }
            content_ios = {'message':
                               {"aps":
                                    {"alert":
                                         {"title": "Funeral Notice",
                                          "subtitle": "",
                                          "body": "Funeral announcement of %s belonging to %s"
                                                  % (name, family_name)},
                                     "sound": "default",
                                     "category": "notice",
                                     "badge": 1,
                                     "mutable-content": 1
                                     },
                                "media-url": image
                                }
                           }
            fcm_messaging_to_all(content)
            apns_messaging_to_all(content_ios)
        except:
            pass
    except:
        pass


@mongo_archive_decorator
def notifications_for_notice_farewell_create(self):
    try:
        name, family_name, image = '', '', ''
        if self.family:
            family_name = self.family.name
            if self.primary_member:
                name = self.primary_member.name
                try:
                    image = settings.DEFAULT_DOMAIN + str(self.primary_member.image.url)
                except:
                    pass
            elif self.secondary_member:
                name = self.secondary_member.member_name
                try:
                    image = settings.DEFAULT_DOMAIN + str(self.secondary_member.image.url)
                except:
                    pass
        else:
            if self.primary_member:
                name = self.primary_member.name
                family_name = self.primary_member.get_file_upload.first().name
                try:
                    image = settings.DEFAULT_DOMAIN + str(self.primary_member.image.url)
                except:
                    pass
            elif self.secondary_member:
                name = self.secondary_member.member_name
                family_name = self.secondary_member.primary_user_id.get_file_upload.first().name
                try:
                    image = settings.DEFAULT_DOMAIN + str(self.secondary_member.image.url)
                except:
                    pass

        if family_name:
            body = {"message": "Farewell Announcement of %s belonging to %s" % (name, family_name),
                    "user_type": "SECONDARY",
                    "type": "farewell",
                    "id": str(self.id)
                    }
        else:
            body = {"message": "Farewell Announcement of %s" % name,
                    "user_type": "SECONDARY",
                    "type": "farewell",
                    "id": str(self.id)
                    }
        notifications = Notification.objects.create(created_time=tz.now(), message=body)
        primary_members = FileUpload.objects.all()
        secondary_members = Members.objects.all()
        for primary_member in primary_members:
            NoticeReadPrimary.objects.create(notification=notifications, user_to=primary_member, is_read=False)
        for secondary_member in secondary_members:
            NoticeReadSecondary.objects.create(notification=notifications, user_to=secondary_member, is_read=False)
        try:
            content = {'title': 'notice title',
                       'message':
                           {
                               "data":
                                   {
                                       "title": "Farewell Notice",
                                       "body": "Farewell announcement of %s belonging to %s" % (name, family_name),
                                       "notificationType": "farewell",
                                       "backgroundImage": image,
                                       "text_type": "long"
                                   },
                               "notification":
                                   {"alert": "This is a FCM notification",
                                    "title": "Farewell Notice",
                                    "body": "Farewell announcement of %s belonging to %s" % (name, family_name),
                                    "sound": "default",
                                    "backgroundImage": image,
                                    "backgroundImageTextColour": "#FFFFFF",
                                    "image": image,
                                    "click_action": "notice"
                                    }
                           }
                       }
            content_ios = {'message':
                               {"aps":
                                    {"alert":
                                         {"title": "Farewell Notice",
                                          "subtitle": "",
                                          "body": "Farewell announcement of %s belonging to %s"
                                                  % (name, family_name)},
                                     "sound": "default",
                                     "category": "notice",
                                     "badge": 1,
                                     "mutable-content": 1
                                     },
                                "media-url": image
                                }
                           }
            fcm_messaging_to_all(content)
            apns_messaging_to_all(content_ios)
        except:
            pass
    except:
        pass


@mongo_archive_decorator
def notifications_for_notice_greeting_create(self):
    body = "You have received a new greeting notice"
    notifications = Notification.objects.create(created_time=tz.now(), message=body)
    primary_members = FileUpload.objects.all()
    secondary_members = Members.objects.all()
    for primary_member in primary_members:
        NoticeReadPrimary.objects.create(notification=notifications, user_to=primary_member, is_read=False)
    for secondary_member in secondary_members:
        NoticeReadSecondary.objects.create(notification=notifications, user_to=secondary_member, is_read=False)
    try:
        if self.image == None and self.video == None and self.audio != None:
            image = "https://cdn0.iconfinder.com/data/icons/cosmo-documents/40/file_audio-512.png"
        elif self.image == None and self.audio == None and self.video != None:
            image = settings.DEFAULT_DOMAIN + str(self.thumbnail.url)
        else:
            image = settings.DEFAULT_DOMAIN + str(self.image.url)
    except:
        image = ""
    try:
        content = {'title': 'notice title',
                   'message':
                       {"data":
                            {"title": "Greeting Notice",
                             "body": str(self.notice),
                             "notificationType": "notice",
                             "backgroundImage": image,
                             "image": image,
                             "text_type": "short"},
                        "notification":
                            {"alert": "This is a FCM notification",
                             "title": "Greeting Notice",
                             "body": str(self.notice),
                             "sound": "default",
                             "backgroundImage": image,
                             "backgroundImageTextColour": "#FFFFFF",
                             "image": image,
                             "click_action": "notice"
                             }
                        }
                   }
        content_ios = {'message':
                           {"aps":
                                {"alert":
                                     {"title": "Greeting Notice",
                                      "subtitle": "",
                                      "body": str(self.notice)
                                      },
                                 "sound": "default",
                                 "category": "notice",
                                 "badge": 1,
                                 "mutable-content": 1
                                 },
                            "media-url": image
                            }
                       }
        fcm_messaging_to_all(content)
        apns_messaging_to_all(content_ios)
    except:
        pass


@mongo_archive_decorator
def notifications_for_group_notice(self):
    body = "You have received a new group notice"
    notifications = Notification.objects.create(created_time=tz.now(), message=body)
    primary_members = self.group.primary_user.all()
    secondary_members = self.group.secondary_user.all()
    try:
        if self.image == None and self.video == None and self.audio != None:
            image = "https://cdn0.iconfinder.com/data/icons/cosmo-documents/40/file_audio-512.png"
        elif self.image == None and self.audio == None and self.video != None:
            image = settings.DEFAULT_DOMAIN + str(self.thumbnail.url)
        else:
            image = settings.DEFAULT_DOMAIN + str(self.image.url)
    except:
        image = ""
    try:
        content = {'title': 'notice title',
                   'message':
                       {"data":
                            {"title": "Notice",
                             "body": str(self.notice),
                             "notificationType": "notice",
                             "backgroundImage": image,
                             "image": image,
                             "text_type": "short"},
                        "notification":
                            {"alert": "This is a FCM notification",
                             "title": "Notice",
                             "body": str(self.notice),
                             "sound": "default",
                             "backgroundImage": image,
                             "backgroundImageTextColour": "#FFFFFF",
                             "image": image,
                             "click_action": "notice"
                             }
                        }
                   }
        content_ios = {'message':
                           {"aps":
                                {"alert":
                                     {"title": "Notice",
                                      "subtitle": "",
                                      "body": str(self.notice)
                                      },
                                 "sound": "default",
                                 "category": "notice",
                                 "badge": 1,
                                 "mutable-content": 1
                                 },
                            "media-url": image
                            }
                       }
    except:
        pass
    for primary_member in primary_members:
        NoticeReadPrimary.objects.create(notification=notifications, user_to=primary_member, is_read=False)
        try:
            user = User.objects.get(username=primary_member.phone_no_primary)
            fcm_messaging_to_user(user, content)
            apns_messaging_to_user(user, content_ios)
        except:
            pass
    for secondary_member in secondary_members:
        NoticeReadSecondary.objects.create(notification=notifications, user_to=secondary_member, is_read=False)
        try:
            user = User.objects.get(username=secondary_member.phone_no_secondary_user)
            fcm_messaging_to_user(user, content)
            apns_messaging_to_user(user, content_ios)
        except:
            pass


def fcm_messaging_to_all(content):
    try:
        device_android = GCMDevice.objects.filter(active=True).exclude(user__is_superuser=True)
        message = content['message']['notification']['body']
        title = content['message']['notification']['title']
        status = device_android.send_message(message,title=title, extra=content['message'])
        return status
    except Exception as exp:
        print("notify",exp)
        return str(exp)


def apns_messaging_to_all(content_ios):
    try:
        device_ios = APNSDevice.objects.filter(active=True).exclude(user__is_superuser=True)
        message_ios = content_ios['message']['aps']['alert']['body']
        title_ios = content_ios['message']['aps']['alert']['title']
        status = device_ios.send_message(message={"title" : title_ios, "body" : message_ios}, extra=content_ios['message'])
        return status
    except Exception as exp:
        print("notify-ios",exp)
        return str(exp)


def fcm_messaging_to_user(user,content):
    # import pdb;pdb.set_trace()
    try:
        device = GCMDevice.objects.filter(user=user,active=True)
        message = content['message']['data']['body']
        title = content['message']['data']['title']
        # del content['data']['data']['body']
        status = device.send_message(message,title=title, extra=content['message'])
        return status
    except Exception as exp:
        print("notify",exp)
        return str(exp)


def apns_messaging_to_user(user,content_ios):
    try:
        device_ios = APNSDevice.objects.filter(user=user,active=True)
        message_ios = content_ios['message']['aps']['alert']['body']
        title_ios = content_ios['message']['aps']['alert']['title']
        status = device_ios.send_message(message={"title" : title_ios, "body" : message_ios}, extra=content_ios['message'])
        return status
    except Exception as exp:
        print("notify-ios",exp)
        return str(exp)


class Notice(models.Model):
    notice = models.CharField(max_length=255)
    description = models.TextField(max_length=10000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    image = models.FileField(upload_to='pan_folder/', null=True, blank=True)
    audio = models.FileField(upload_to='audio_files/', null=True, blank=True)
    video = models.FileField(upload_to='video_files/', null=True, blank=True)
    thumbnail = models.FileField(upload_to='thumbnails/', null=True, blank=True)


class FileUpload(models.Model):
    primary_user_id = models.AutoField(max_length=5, primary_key=True)
    name = models.CharField(max_length=200)
    password = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='1')
    group_position = models.CharField(max_length=20, null=True, blank=True)
    image = models.FileField(upload_to='members/', null=True, blank=True)
    current_address = models.TextField(max_length=500, null=True, blank=True)
    residential_address = models.TextField(max_length=500, null=True, blank=True)
    permanent_address = models.TextField(max_length=500, null=True, blank=True)
    parish_name = models.TextField(max_length=500, null=True, blank=True)
    phone_no_primary = models.CharField(max_length=20, null=True, blank=True)
    phone_no_secondary = models.CharField(max_length=20, null=True, blank=True)
    dob = models.CharField(max_length=20, null=True, blank=True)
    dom = models.CharField(max_length=20, null=True, blank=True)
    blood_group = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    occupation = models.TextField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    marital_status = models.CharField(max_length=20,null=True,blank=True)
    marrige_date = models.CharField(max_length=20,null=True,blank=True)
    in_memory = models.BooleanField(default=False)
    in_memory_date =models.DateTimeField(null=True, blank=True)
    relation = models.CharField(max_length=255, null=True, blank=True)
    landline = models.CharField(max_length=20, null=True, blank=True)


    def __str__(self):
        return self.name


class Family(models.Model):
    name = models.CharField(verbose_name="Membership_id", max_length=20, unique=True)
    about = models.TextField(null=True, blank=True)
    image = models.FileField(upload_to='familyimage/', null=True, blank=True)
    members_length = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    primary_user_id = models.ForeignKey(FileUpload, on_delete=models.CASCADE, related_name='get_file_upload', null=True,
                                        blank=True)

    class Meta:
        verbose_name = 'Membership'
        verbose_name_plural = 'Memberships'

    def __str__(self):
        return self.name


class Members(models.Model):
    secondary_user_id = models.AutoField(max_length=5, primary_key=True)
    member_name = models.CharField(max_length=255)
    password = models.CharField(max_length=20, null=True, blank=True)
    group_position = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='1')
    current_address = models.TextField(max_length=500, null=True, blank=True)
    residential_address = models.TextField(max_length=500, null=True, blank=True)
    permanent_address = models.TextField(max_length=500, null=True, blank=True)
    parish_name = models.TextField(max_length=500, null=True, blank=True)
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
    occupation =models.TextField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    marital_status = models.CharField(max_length=20,null=True,blank=True)
    marrige_date = models.CharField(max_length=20,null=True,blank=True)
    in_memory = models.BooleanField(default=False)
    in_memory_date = models.DateTimeField(null=True, blank=True)
    landline = models.CharField(max_length=20, null=True, blank=True)

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
    occupation = models.TextField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    marital_status = models.CharField(max_length=20,null=True,blank=True)
    marrige_date = models.CharField(max_length=20,null=True,blank=True)
    in_memory = models.BooleanField(default=False)
    in_memory_date = models.DateTimeField(null=True, blank=True)
    rejected = models.BooleanField(default=False)
    edit_user = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=200, null=True, blank=True)
    date=models.DateTimeField(default=datetime.now, blank=True)
    landline = models.CharField(max_length=20, null=True, blank=True)
    
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
    audio = models.FileField(upload_to='audio_files/', null=True, blank=True)
    video = models.FileField(upload_to='video_files/', null=True, blank=True)
    thumbnail = models.FileField(upload_to='thumbnails/', null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        notifications_for_notice(self)


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
    image = models.FileField(verbose_name="Image / Video", upload_to='pan_folder/')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    date = models.DateField(default=timezone.now)

    class Meta:
        verbose_name = 'Image / Video'
        verbose_name_plural = 'Images / Videos'

class ChurchDetails(models.Model):
    church_name = models.CharField(max_length=200)
    description = models.TextField(max_length=5000, null=True, blank=True)
    our_church = models.TextField(max_length=5000, null=True, blank=True)
    infrastructure = models.TextField(max_length=5000, null=True, blank=True)
    organization = models.TextField(max_length=5000, null=True, blank=True)
    church_place = models.CharField(max_length=200)
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
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated = models.BooleanField(default=False)
    description = models.TextField(max_length=10000, null=True, blank=True)
    prayer_group = models.ForeignKey(PrayerGroup, on_delete=models.CASCADE, null=True, blank=True)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True, blank=True)
    primary_member = models.ForeignKey(FileUpload, on_delete=models.CASCADE, null=True, blank=True)
    secondary_member = models.ForeignKey(Members, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.id:
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
            notifications_for_notice_bereavement_create(self)


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


MOBILE = 'mobile'
FAMILY = 'family'
REQUEST_TYPE = (
    (MOBILE, 'MOBILE'),
    (FAMILY, 'FAMILY'),
)

PRIMARY = 'primary'
SECONDARY = 'secondary'

USER_TYPES = (
    (PRIMARY, 'PRIMARY'),
    (SECONDARY, 'SECONDARY'),
)

class ChangeRequest(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    request_type = models.CharField(max_length=255, choices=REQUEST_TYPE)
    user_id = models.IntegerField(null=True, blank=True)
    user_type = models.CharField(max_length=255, choices=USER_TYPES, null=True, blank=True)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    user_name = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(max_length=20000)

VICAR = 'vicar'
ASSTVICAR = 'asstvicar'

VICAR_TYPES = (
    (VICAR, 'VICAR'),
    (ASSTVICAR, 'ASSTVICAR'),
)

class ChurchVicars(models.Model):
    vicar_name = models.CharField(max_length=100)
    vicar_info = models.TextField(max_length=1000, null=True, blank=True)
    vicar_image = models.FileField(upload_to='pan_folder/', null=True, blank=True)
    start_year = models.CharField(max_length=10,null=True, blank=True)
    end_year = models.CharField(max_length=10,null=True, blank=True)
    vicar_type = models.CharField(max_length=10,choices=VICAR_TYPES,null=True, blank=True)


class HonourAndRespect(models.Model):
    title = models.CharField(max_length=200)
    image = models.FileField(upload_to='pan_folder/', null=True, blank=True)
    description = models.TextField(max_length=10000, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.title


class NoticeFarewell(models.Model):
    # title = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated = models.BooleanField(default=False)
    description = models.TextField(max_length=100, null=True, blank=True)
    prayer_group = models.ForeignKey(PrayerGroup, on_delete=models.CASCADE, null=True, blank=True)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True, blank=True)
    primary_member = models.ForeignKey(FileUpload, on_delete=models.CASCADE, null=True, blank=True)
    secondary_member = models.ForeignKey(Members, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.id:
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
            notifications_for_notice_farewell_create(self)


class NoticeGreeting(models.Model):
    notice = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated = models.BooleanField(default=False)
    description = models.TextField(max_length=100, null=True, blank=True)
    prayer_group = models.ForeignKey(PrayerGroup, on_delete=models.CASCADE, null=True, blank=True)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True, blank=True)
    primary_member = models.ManyToManyField(FileUpload, null=True, blank=True)
    secondary_member = models.ManyToManyField(Members, null=True, blank=True)
    image = models.FileField(upload_to='pan_folder/', null=True, blank=True)
    audio = models.FileField(upload_to='audio_files/', null=True, blank=True)
    video = models.FileField(upload_to='video_files/', null=True, blank=True)
    thumbnail = models.FileField(upload_to='thumbnails/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.id:
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
            notifications_for_notice_greeting_create(self)


class Group(models.Model):
    group_name = models.CharField(max_length=200)
    group_image = models.FileField(upload_to='pan_folder/', null=True, blank=True)
    group_description = models.TextField(max_length=10000, null=True, blank=True)
    primary_user = models.ManyToManyField(FileUpload, null=True, blank=True)
    secondary_user = models.ManyToManyField(Members, null=True, blank=True)

    def __str__(self):
        return self.group_name


class GroupNotice(models.Model):
    notice = models.CharField(max_length=255, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    description = models.TextField(max_length=10000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    image = models.FileField(upload_to='pan_folder/', null=True, blank=True)
    audio = models.FileField(upload_to='audio_files/', null=True, blank=True)
    video = models.FileField(upload_to='video_files/', null=True, blank=True)
    thumbnail = models.FileField(upload_to='thumbnails/', null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        notifications_for_group_notice(self)


class ActiveUser(models.Model):
    name = models.CharField(max_length=200)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    membership_id = models.CharField(max_length=20, null=True, blank=True)
    last_login = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class InactiveUser(models.Model):
    name = models.CharField(max_length=200)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    membership_id = models.CharField(max_length=20)
