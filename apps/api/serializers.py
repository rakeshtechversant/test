from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
import requests
from apps.church.models import UserProfile, ChurchDetails, FileUpload, OtpModels, \
    OtpVerify, PrayerGroup, Notification, Family, Members, Notice, NoticeBereavement, \
    UnapprovedMember, NoticeReadPrimary, NoticeReadSecondary, NoticeReadAdmin, ViewRequestNumber, PrivacyPolicy, \
    PhoneVersion, Images, PrimaryToSecondary, NumberChangePrimary, ChangeRequest, ChurchVicars
from rest_framework.serializers import CharField
from apps.api.token_create import get_tokens_for_user
from django.utils.crypto import get_random_string
from twilio.rest import Client
from django.http import HttpResponseRedirect
from church_project import settings
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.response import Response
from datetime import datetime
import pytz
from apps.api.models import AdminProfile
from django.utils import timezone as tz
from push_notifications.models import APNSDevice, GCMDevice

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


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','password','email']



class UserRegistrationMobileSerializer(serializers.ModelSerializer):
    class Meta:
        model=OtpModels
        fields = ['mobile_number']


class UserCreateSerializer(serializers.ModelSerializer):
    # token = CharField(allow_blank=True, read_only=True)
    # refresh_token = CharField(allow_blank=True, read_only=True)
    user_name = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()
    class Meta:
        model = UserProfile
        fields = ['user_name','password','confirm_password']


    # def validate(self, data):
    #     user_count=0
    #     mobile_number = data.get("mobile_number", None)
    #     username=data.get("user")['username']
    #     password=data.get("user")['password']
    #     if not password or not username:
    #         raise serializers.ValidationError("This field is required")
    #     if User.objects.filter(username=username).exists():
    #         raise serializers.ValidationError("Username already exists")


    #         # message = "OTP for login is %s" % (otp_number,)
    #         # requests.get(
    #         #         "http://unifiedbuzz.com/api/insms/format/json/?mobile=" + mobile_number + "&text=" + message +
    #         #         "&flash=0&type=1&sender=MARCHR",
    #         #         headers={"X-API-Key": "918e0674e62e01ec16ddba9a0cea447b"})
    #     return data

class FamilyListSerializer(serializers.ModelSerializer):
    members_length = serializers.SerializerMethodField()
    class Meta:
        model = Family
        fields = ['name','members_length','image','id','active']

    def to_representation(self, obj):
        data = super().to_representation(obj)
        try:
            data['name'] = obj.name.title()
        except:
            pass
        return data

    def get_members_length(self, obj):
            try:
                name = obj.primary_user_id
                number_list = Members.objects.filter(primary_user_id=name.primary_user_id).count()
                number_list = number_list + 1
            except:
                number_list = 0
            return number_list

class FamilyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=Family
        fields = ['name','members_length','image','id','about']

class FamilyEditSerializer(serializers.ModelSerializer):
    class Meta:
        model=Family
        fields = ['image','about']

class UserRetrieveSerializer(serializers.ModelSerializer):
    family_name = serializers.SerializerMethodField()
    class Meta:
        model = FileUpload
        fields = '__all__'

    def get_family_name(self, obj):
            try:
                name = obj.get_file_upload.get().name
            except:
                name = None
            return name

    def to_representation(self, instance):
        # import pdb;pdb.set_trace()
        data = super().to_representation(instance)
        request = self.context['request']
        data['user_type'] = 'PRIMARY'
        data['user_id'] = instance.primary_user_id
        # data['user_id'] = data.pop('primary_user_id')
        try:
            data['name'] = obj.name.title()
        except:
            pass

        try :
            data['image'] = request.build_absolute_uri(instance.image.url)
        except:
            data['image'] = None
        try:
            data['family_id'] = instance.get_file_upload.get().id
        except:
            data['family_id'] = None
        try:
            data['active'] = instance.get_file_upload.get().active
        except:
            data['active'] = None
        return data




class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = FileUpload
        fields = ['primary_user_id','name','address','phone_no_primary','phone_no_secondary','dob','dom','blood_group','email','occupation','about','marital_status']



class ChurchVicarSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurchDetails
        fields = ['vicar_inf','vicar_image','vicar_name']

class ChurchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurchDetails
        fields = ['description','cover_image','church_name','address','image']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context['request']

        images = instance.image.all()

        data['image'] = []
        
        for image in images:
            image_url = request.build_absolute_uri(image.image.url)

            data['image'].append({
                    'image_url': image_url,
                    'title': image.category,
                    'date': image.date
                }
            )

        return data

    

class ChurchImagesSerializer(serializers.ModelSerializer):

    image=serializers.SerializerMethodField()

    class Meta:
        model = ChurchDetails
        fields = ['image']
        # lookup_field = 'image'

    # def get_image(self, obj):
    #     images = obj.image.all()
    #     url_lst = []
    #     request = self.context['request']
    #     for image in images:
    #         url_lst.append(request.build_absolute_uri(image.image.url))
    #     return url_lst

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['user','first_name','last_name']


class OTPVeifySerializer(serializers.ModelSerializer):
    user_type = serializers.CharField()
    user_id = serializers.CharField()

    class Meta:
        model = OtpVerify
        fields = ['otp','user_type']


class OTPVeifySerializerUserId(serializers.ModelSerializer):
    user_type = serializers.CharField()
    user_id = serializers.CharField()
    phone_number = serializers.CharField()

    class Meta:
        model = OtpVerify
        fields = ['otp','user_type','user_id','phone_number']

class SecondaryaddSerializer(serializers.ModelSerializer):

    class Meta:
        model = FileUpload
        # read_only_fields = ('user',)


class PrayerGroupAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrayerGroup
        fields = ['name','id']

class PrayerGroupAddMembersSerializer(serializers.ModelSerializer):
    user_profile = serializers.PrimaryKeyRelatedField(queryset=FileUpload.objects.all(), many=True,read_only=False)
    class Meta:
        model = PrayerGroup
        fields = ['user_profile']
        read_only_fields = ('name',)



class LoginSerializer(serializers.ModelSerializer):
    """Serializer to login an user thorugh API
    """
    class Meta:
        model = User
        fields = ['username','password']

class MembersSerializer(serializers.ModelSerializer):
    primary_name = serializers.SerializerMethodField()
    phone_no_primary = serializers.SerializerMethodField()
    in_memory_date = serializers.SerializerMethodField()

    # family_

    class Meta:
        model = Members
        fields = ['phone_no_primary','primary_name','secondary_user_id','member_name','relation','dob','dom','image','phone_no_secondary_user','primary_user_id','in_memory','in_memory_date','occupation']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['name'] = data.pop('member_name')
        data['user_type'] = 'SECONDARY'
        data['user_id'] = instance.secondary_user_id
        request = self.context['request']
        try:
            data['member_name'] = obj.member_name.title()
        except:
            pass
        try:
            data['about'] = instance.about
        except:
            pass
        try :
            data['image'] = request.build_absolute_uri(instance.image.url)
        except:
            data['image'] = None
        try:
            data['family_id'] = instance.primary_user_id.get_file_upload.first().id
        except:
            data['family_id'] = None
        try:
            data['family_name'] = instance.primary_user_id.get_file_upload.first().name
        except:
            data['family_name'] = None
        try:
            data['active'] = instance.primary_user_id.get_file_upload.first().active
        except:
            data['active'] = None

        try:
            data['phone_no_secondary_user_secondary'] = instance.phone_no_secondary_user
        except:
            data['phone_no_secondary_user_secondary'] = None

        try:
            if instance.in_memory:
                try:
                    data['in_memory_date_format'] = tz.localtime(instance.in_memory_date, pytz.timezone('Asia/Kolkata')).strftime("%d/%m/%Y")
                except:
                    data['in_memory_date_format'] = instance.in_memory_date.strftime("%d/%m/%Y")
            else:
                data['in_memory_date_format'] = None
        except:
            data['in_memory_date_format'] = None
        return data



    def get_in_memory_date(self, obj):
        date = obj.in_memory_date
        if date:
            return date
        else:
            return None

    def get_primary_name(self, obj):
        name = obj.primary_user_id.name
        if name:
            serializer = UserRetrieveSerializer(name,context=self.context)
            return name
        return None

    def get_phone_no_primary(self, obj):
        primary_number = obj.primary_user_id.phone_no_primary
        if primary_number:
            serializer = UserRetrieveSerializer(primary_number)
            return primary_number
        return None


class NoticeSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d/%m/%Y %I:%M %p", read_only=True)
    updated_at = serializers.DateTimeField(format="%d/%m/%Y %I:%M %p", read_only=True)

    class Meta:
        model = Notice
        fields = '__all__'

    def create(self, validated_data):
        notice = Notice(**validated_data)
        notice.save()
        body= {"message":"You have received a new notice",
                            "type":"notice",
                            "id":str(notice.id)
                            }

        body="You have received a new notice"
        notifications=Notification.objects.create(created_time=tz.now(),message=body)
        primary_members=FileUpload.objects.all()
        secondary_members=Members.objects.all()
        for primary_member in primary_members:
            NoticeReadPrimary.objects.create(notification=notifications,user_to=primary_member,is_read=False)
        for secondary_member in secondary_members:
            NoticeReadSecondary.objects.create(notification=notifications,user_to=secondary_member,is_read=False)

        try:
            request = self.context['request']
            # image = "https://cdn1.iconfinder.com/data/icons/mobile-application-2-solid/128/notification_alert_alarm-512.png"
            if notice.image == None and notice.video == None and notice.audio != None:
                image = "https://cdn0.iconfinder.com/data/icons/cosmo-documents/40/file_audio-512.png"
            elif notice.image == None and notice.audio == None and notice.video != None:
                image= request.build_absolute_uri(notice.thumbnail.url)
            else:
                image= request.build_absolute_uri(notice.image.url)
        except:
            image = ""
        try:
            content = {'title':'notice title','message':{"data":{"title":"Notice","body":str(notice.notice),"notificationType":"notice","backgroundImage":image,"image":image,"text_type":"short"},\
            "notification":{"alert":"This is a FCM notification","title":"Notice","body":str(notice.notice),"sound":"default","backgroundImage":image,"backgroundImageTextColour":"#FFFFFF","image":image,"click_action":"notice"}}}
            content_ios = {'message':{"aps":{"alert":{"title":"Notice","subtitle":"","body":str(notice.notice)},"sound":"default","category":"notice","badge":1,"mutable-content":1},"media-url":image}}
            resp = fcm_messaging_to_all(content)
            resp1 = apns_messaging_to_all(content_ios)
        except:
            pass
        return notice

    def update(self,instance, validated_data):
        instance = super().update(instance, validated_data)
        if validated_data.get('audio') != None:
            instance.image = None
            instance.video = None
            instance.thumbnail = None
        elif validated_data.get('video') != None:
            instance.image = None
            instance.audio = None
        elif validated_data.get('image') != None:
            instance.video = None
            instance.audio = None
            instance.thumbnail = None
        else:
            pass
        instance.save()
        
        # body="A notice has been modified"
        # body= {"message":"A notice has been modified",
        #                     "type":"notice",
        #                     "id":str(instance.id)
        #     }
        # notifications=Notification.objects.create(created_time=tz.now(),message=body)
        # primary_members=FileUpload.objects.all()
        # secondary_members=Members.objects.all()
        # for primary_member in primary_members:
        #     NoticeReadPrimary.objects.create(notification=notifications,user_to=primary_member,is_read=False)
        # for secondary_member in secondary_members:
        #     NoticeReadSecondary.objects.create(notification=notifications,user_to=secondary_member,is_read=False)
        
        return instance


class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminProfile
        fields = ['mobile_number']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['user_type'] = 'ADMIN'

        return data


class PrimaryUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = '__all__'
        read_only_fields = ['phone_no_primary']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['user_type'] = 'PRIMARY'

        request = self.context['request']
        try :
            data['image'] = request.build_absolute_uri(instance.image.url)
        except:
            data['image'] = None
        try :
            data['name'] = instance.name.title()
        except:
            pass
        try :
            data['primary_user_name'] = instance.name.title()
        except:
            pass
        try:
            data['family_name'] = instance.get_file_upload.first().name
        except:
            data['family_name'] = None
        try:
            data['family_id'] = instance.get_file_upload.first().id
        except:
            data['family_id'] = None
        try :
            if instance.marrige_date :
                data['marrige_date'] = instance.marrige_date
            elif instance.dom:
                data['marrige_date'] = instance.dom
            else:
                data['marrige_date'] = None
        except:
            data['marrige_date'] = None
        return data



class NoticeBereavementSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d/%m/%Y %I:%M %p", read_only=True)
    updated_at = serializers.DateTimeField(format="%d/%m/%Y %I:%M %p")
    class Meta:
        model=NoticeBereavement
        fields = '__all__'


class MemberProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Members
        fields = '__all__'
        read_only_fields = ['phone_no_secondary_user']
    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['user_type'] = 'SECONDARY'

        request = self.context['request']

        try :
            data['image'] = request.build_absolute_uri(instance.image.url)
        except:
            data['image'] = None

        try :
            data['name'] = instance.member_name.title()
        except:
            data['name'] = None
        try :
            data['primary_user_name'] = instance.primary_user_id.name.title()
        except:
            data['primary_user_name'] = None
        try :
            data['primary_name'] = instance.primary_user_id.name
        except:
            data['primary_name'] = None
            
        try :
            data['phone_no_primary'] = instance.phone_no_secondary_user
        except:
            data['phone_no_primary'] = None

        try :
            data['phone_no_secondary'] = instance.phone_no_secondary_user_secondary
        except:
            data['phone_no_secondary'] = None

        try :
            data['primary_in_memory'] = instance.primary_user_id.in_memory
        except:
            data['primary_in_memory'] = None

        try:
            data['family_name'] = instance.primary_user_id.get_file_upload.first().name
        except:
            data['family_name'] = None
        try:
            data['family_id'] = instance.primary_user_id.get_file_upload.first().id
        except:
            data['family_id'] = None
        try :
            if instance.marrige_date :
                data['marrige_date'] = instance.marrige_date
            elif instance.dom:
                data['marrige_date'] = instance.dom
            else:
                data['marrige_date'] = None
        except:
            data['marrige_date'] = None
        return data



class UserDetailsRetrieveSerializer(serializers.ModelSerializer):
    in_memory_date = serializers.SerializerMethodField()
    # family_name = serializers.SerializerMethodField()
    # family_description = serializers.SerializerMethodField()
    class Meta:
        model = FileUpload
        fields = ['primary_user_id','image','name','address','phone_no_primary','phone_no_secondary','dob','dom','blood_group','email','in_memory','in_memory_date','occupation','about','relation']

    def get_in_memory_date(self, obj):
        date = obj.in_memory_date
        if date:
            return date
        else:
            return None

    def to_representation(self, instance):
        # import pdb;pdb.set_trace()
        data = super().to_representation(instance)
        request = self.context['request']
        try :
            data['image'] = request.build_absolute_uri(instance.image.url)
        except:
            data['image'] = None
        data['user_id'] = instance.primary_user_id
        try: 
            data['name'] = instance.name.title()
        except:
            pass
        try: 
            data['landline'] = instance.landline
        except:
            data['landline'] = None
        data['user_type'] = 'PRIMARY'
        try:
            if instance.in_memory:
                try:
                    data['in_memory_date_format'] = tz.localtime(instance.in_memory_date, pytz.timezone('Asia/Kolkata')).strftime("%d/%m/%Y")
                except:
                    data['in_memory_date_format'] = instance.in_memory_date.strftime("%d/%m/%Y")
            else:
                data['in_memory_date_format'] = None
        except:
            data['in_memory_date_format'] = None
        try :
            if instance.marrige_date :
                data['dom'] = instance.marrige_date
            elif instance.dom:
                data['dom'] = instance.dom
            else:
                data['dom'] = None
        except:
            data['dom'] = None

        try :
            if instance.marrige_date :
                data['marrige_date'] = instance.marrige_date
            elif instance.dom:
                data['marrige_date'] = instance.dom
            else:
                data['marrige_date'] = None
        except:
            data['marrige_date'] = None

        try:
            data['family_id'] = instance.get_file_upload.first().id
        except:
            data['family_id'] = None
        try:
            data['family_name'] = instance.get_file_upload.first().name
        except:
            data['family_name'] = None
        return data

    # def get_family_name(self, obj):
    #     try:
    #         name = obj.get_file_upload.get().name
    #     except:
    #         name = None
    #     return name

    # def get_family_description(self, obj):
    #     try:
    #         about = obj.get_file_upload.get().about
    #     except:
    #         about = None
    #     return about

class MembersDetailsSerializer(serializers.ModelSerializer):
    primary_name = serializers.SerializerMethodField()
    phone_no_primary = serializers.SerializerMethodField()
    in_memory_date = serializers.SerializerMethodField()

    class Meta:
        model = Members
        fields = ['phone_no_primary','primary_name','secondary_user_id','member_name','relation','dob','dom','image','phone_no_secondary_user','primary_user_id','in_memory','in_memory_date','occupation','about']

    def get_in_memory_date(self, obj):
        date = obj.in_memory_date
        if date:
            return date
        else:
            return None

    def get_primary_name(self, obj):
        primary_user = obj.primary_user_id
        if primary_user:
            if primary_user.name:
                serializer = UserDetailsRetrieveSerializer(primary_user.name)
                return primary_user.name
        return None

    def get_phone_no_primary(self, obj):
        primary_user = obj.primary_user_id

        if primary_user:
            if primary_user.phone_no_primary:

                serializer = UserDetailsRetrieveSerializer(primary_user.phone_no_primary)
                return primary_user.phone_no_primary
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context['request']
        try:
            data['member_name'] = instance.member_name.title()
        except:
            pass
        data['name'] = data.pop('member_name')
        data['user_id'] = instance.secondary_user_id
        data['user_type'] = 'SECONDARY'
        try :
            data['image'] = request.build_absolute_uri(instance.image.url)
        except:
            data['image'] = None
        try: 
            data['landline'] = instance.landline
        except:
            data['landline'] = None
        try: 
            data['blood_group'] = instance.blood_group
        except:
            data['blood_group'] = None
        try :
            if instance.marrige_date :
                data['dom'] = instance.marrige_date
            elif instance.dom:
                data['dom'] = instance.dom
            else:
                data['dom'] = None
        except:
            data['dom'] = None
        try :
            if instance.marrige_date :
                data['marrige_date'] = instance.marrige_date
            elif instance.dom:
                data['marrige_date'] = instance.dom
            else:
                data['marrige_date'] = None
        except:
            data['marrige_date'] = None
        try:
            data['phone_no_secondary_user_secondary']=instance.phone_no_secondary_user_secondary
        except:
            data['phone_no_secondary_user_secondary'] = None
        try:
            if instance.in_memory:
                try:
                    data['in_memory_date_format'] = tz.localtime(instance.in_memory_date, pytz.timezone('Asia/Kolkata')).strftime("%d/%m/%Y")
                except:
                    data['in_memory_date_format'] = instance.in_memory_date.strftime("%d/%m/%Y")
            else:
                data['in_memory_date_format'] = None
        except:
            data['in_memory_date_format'] = None
        return data


class UnapprovedMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = UnapprovedMember
        exclude = ['primary_user_id', 'rejected', 'edit_user']

    def create(self, validated_data):

        created_by = self.context['request'].user

        primary_user = FileUpload.objects.get(phone_no_primary=created_by.username)

        unapproved_member = UnapprovedMember(**validated_data)
        unapproved_member.primary_user_id = primary_user
        unapproved_member.save()

        # notification = Notification.objects.create(
        #     created_by_primary=primary_user, 
        #     message="User %s added a family member %s. Verify and approve to reflect changes"%(primary_user, unapproved_member)
        # )
        user_details={
            "notification_id":unapproved_member.secondary_user_id,
            "primary_name":primary_user.name,
            "primary_id":primary_user.primary_user_id,
            "secondary_name":unapproved_member.member_name,
            "primary_phone_number":primary_user.phone_no_primary,
            "family_name":primary_user.get_file_upload.first().name,
            "prayer_group_name":primary_user.get_file_upload_prayergroup.first().name,
            "send_time":str(tz.now()),
            "type":"primary_add_secondary",
        }

        user_details_str=str(user_details)
        notification = Notification.objects.create(
            created_by_primary=primary_user, 
            message=user_details_str
        )
        admin_profiles = AdminProfile.objects.all()

        for admin_profile in admin_profiles:
            NoticeReadAdmin.objects.create(notification=notification, user_to=admin_profile)
        try:
            request = self.context['request']
            image= request.build_absolute_uri(unapproved_member.image.url)
        except:
            image = ""
        try:
            for admin_profile in admin_profiles:
                content = {'title':'New Member Request','message':{"data":{"title":"New Member Request","body":"%s,of %s,%s has requested to add a family member %s"%(primary_user,str(primary_user.get_file_upload.first().name),str(primary_user.get_file_upload_prayergroup.first().name), unapproved_member),"notificationType":"request","backgroundImage":image,"text_type":"long"},\
                "notification":{"alert":"This is a FCM notification","title":"New Member Request","body":"%s,of %s,%s has requested to add a family member %s"%(primary_user,str(primary_user.get_file_upload.first().name),str(primary_user.get_file_upload_prayergroup.first().name),unapproved_member),"sound":"default","backgroundImage":image,"backgroundImageTextColour":"#FFFFFF","image":image,"click_action":"request"}} } 

                content_ios = {'message':{"aps":{"alert":{"title":"New Member Request","subtitle":"","body":"%s,of %s,%s has requested to add a family member %s"%(primary_user,str(primary_user.get_file_upload.first().name),str(primary_user.get_file_upload_prayergroup.first().name), unapproved_member)},"sound":"default","category":"request","badge":1,"mutable-content":1},"media-url":image}}
                resp = fcm_messaging_to_user(admin_profile.user,content)
                resp1 = apns_messaging_to_user(admin_profile.user,content_ios)
        except:
            pass
        return unapproved_member

    def update(self, instance, validated_data):

        created_by = self.context['request'].user
        primary_user = FileUpload.objects.get(phone_no_primary=created_by.username)

        instance = super().update(instance, validated_data)
        instance.rejected = False
        instance.edit = True
        instance.save()

        notification = Notification.objects.create(
            created_by_primary=primary_user, 
            message="User %s updated a family member %s. Verify and approve to reflect changes"%(primary_user, instance)
        )

        admin_profiles = AdminProfile.objects.all()
        
        for admin_profile in admin_profiles:
            NoticeReadAdmin.objects.create(notification=notification, user_to=admin_profile)

        return instance

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data['rejected'] = obj.rejected
        data['primary_user_id'] = obj.primary_user_id.primary_user_id
        data['primary_user_number'] = obj.primary_user_id.phone_no_primary
        data['primary_user_name'] = obj.primary_user_id.name
        data['edit_user'] = obj.edit_user
        try:
            data['family_name'] = FileUpload.objects.get(primary_user_id=obj.primary_user_id.primary_user_id).get_file_upload.first().name
        except:
            data['family_name'] = None

        try:
            data['prayer_group_name'] = FileUpload.objects.get(primary_user_id=obj.primary_user_id.primary_user_id).get_file_upload_prayergroup.first().name
        except:
            data['prayer_group_name'] = None

        try:
            data['type'] = 'primary_add_secondary'
        except:
            data['type'] = None

        data['date'] = obj.date
        try:
            data['date_format'] = tz.localtime(obj.date, pytz.timezone('Asia/Kolkata')).strftime("%d/%m/%Y, %H:%M:%S %p")
        except:
            data['date_format'] = obj.date.strftime("%d/%m/%Y, %H:%M:%S %p")
        try:
            if obj.status:
                data['status'] = obj.status
            else:
                data['status'] = 'Pending'
        except:
            data['status'] = 'Pending'
        return data


class MemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = Members
        fields = '__all__'
        read_only_fields = ['secondary_user_id']

    def to_representation(self, obj):

        data = super().to_representation(obj)

        request = self.context['request']

        if obj.primary_user_id:
            try:
                data['family_name'] = obj.primary_user_id.get_file_upload.first().name.title()
            except:
                data['family_name'] = ''

        else:
            data['family_name' ] = ''

        try:
            data['member_name'] = obj.member_name.title()
        except:
            pass

        if obj.image:
            try :
                data['image'] = request.build_absolute_uri(obj.image.url)
            except:
                data['image'] = None

        data['user_type'] = 'secondary'

        return data


class PrimaryUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = '__all__'
        read_only_fields = ['primary_user_id']

    def to_representation(self, obj):

        data = super().to_representation(obj)

        request = self.context['request']

        if obj.get_file_upload.first():
            data['family_name'] = obj.get_file_upload.first().name.title()
        else:
            data['family_name'] = ''

        try:
            data['name'] = obj.name.title()
        except:
            pass

        if obj.image:
            try :
                data['image'] = request.build_absolute_uri(obj.image.url)
            except:
                data['image'] = None

        data['user_type'] = 'primary'

        return data


class UserByadminSerializer(serializers.Serializer):
    prayer_group = serializers.PrimaryKeyRelatedField(queryset=PrayerGroup.objects.all())
    family = serializers.PrimaryKeyRelatedField(queryset=Family.objects.all())
    name = serializers.CharField()
    blood_group = serializers.CharField(allow_blank=True,required=False)
    dob = serializers.CharField(allow_blank=True,required=False)
    email = serializers.EmailField(allow_blank=True,required=False)
    primary_number = serializers.CharField(allow_blank=True,required=False)
    secondary_number = serializers.CharField(allow_blank=True,required=False)
    occupation = serializers.CharField(allow_blank=True,required=False)
    relation =  serializers.CharField(allow_blank=True,required=False)
    marital_status = serializers.CharField(allow_blank=True,required=False)
    marrige_date = serializers.CharField(allow_blank=True,required=False)
    member_type = serializers.CharField()
    member_status = serializers.ChoiceField(choices=['active', 'in_memory'])
    about = serializers.CharField(allow_blank=True,required=False)
    landline = serializers.CharField(allow_blank=True,required=False)

class UserByMembersSerializer(serializers.Serializer):
    prayer_group = serializers.PrimaryKeyRelatedField(queryset=PrayerGroup.objects.all())
    family = serializers.PrimaryKeyRelatedField(queryset=Family.objects.all())
    name = serializers.CharField()
    blood_group = serializers.CharField(allow_blank=True,required=False)
    dob = serializers.CharField(allow_blank=True,required=False)
    email = serializers.EmailField(allow_blank=True,required=False)
    primary_number = serializers.CharField(allow_blank=True,required=False)
    secondary_number = serializers.CharField(allow_blank=True,required=False)
    occupation = serializers.CharField(allow_blank=True,required=False)
    relation =  serializers.CharField(allow_blank=True,required=False)
    marital_status = serializers.CharField(allow_blank=True,required=False)
    marrige_date = serializers.CharField(allow_blank=True,required=False)
    member_type = serializers.CharField()
    member_status = serializers.ChoiceField(choices=['active', 'in_memory'])
    about = serializers.CharField(allow_blank=True,required=False)
    landline = serializers.CharField(allow_blank=True,required=False)


class FamilyByadminSerializer(serializers.Serializer):
    prayer_group = serializers.PrimaryKeyRelatedField(queryset=PrayerGroup.objects.all(), allow_null=True)
    family_name = serializers.CharField()


class PrimaryNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model=NoticeReadPrimary
        fields='__all__'
    def to_representation(self, obj):
        data={'message':obj.notification.message}

        return data

class SecondaryNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model=NoticeReadSecondary
        fields='__all__'
    def to_representation(self, obj):
        data={'message':obj.notification.message}

        return data

class AdminNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model=NoticeReadAdmin
        fields='__all__'

    def to_representation(self, obj):
        data={'message':obj.notification.message}

        return data

class ViewRequestNumberSerializer(serializers.ModelSerializer):

    class Meta:
        model = ViewRequestNumber
        fields = ['request_from', 'request_to','usertype_to','usertype_from']


class RequestAcceptNumberSerializer(serializers.ModelSerializer):
    is_accepted = serializers.BooleanField(write_only=True)
    # notification_id = serializers.PrimaryKeyRelatedField(queryset=Notification.objects.all())
    class Meta:
        model = ViewRequestNumber
        fields = ['request_from', 'request_to','usertype_to','usertype_from','is_accepted']


class PrivacyPolicy(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = '__all__'

class PhoneVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneVersion
        fields = '__all__'


class GalleryImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model= Images
        fields = '__all__'

class GalleryImagesCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model= Images
        fields = ['image','category','title','date']



class CommonUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    name=serializers.CharField()
    image=serializers.CharField()
    address=serializers.CharField()
    phone_no_primary=serializers.CharField()
    phone_no_secondary=serializers.CharField()
    dob=serializers.CharField()
    dom=serializers.CharField()
    blood_group=serializers.CharField()
    email=serializers.CharField()
    occupation=serializers.CharField()
    about=serializers.CharField()
    marital_status=serializers.CharField()
    in_memory=serializers.CharField()
    in_memory_date=serializers.CharField()
    family_name=serializers.CharField()
    active=serializers.BooleanField()
    family_id=serializers.IntegerField()
    user_type=serializers.CharField()
    relation=serializers.CharField()
    primary_user_id=serializers.IntegerField()
    primary_name=serializers.CharField()


class MemberNumberSerializer(serializers.Serializer):
    phone_no_secondary_user=serializers.CharField(required=False)
    phone_no_secondary_user_secondary=serializers.CharField(required=False)
    class Meta:
        model = Members
        fields = '__all__'


class PrimaryToSecondarySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrimaryToSecondary
        fields = ['request_from', 'request_to','usertype_from','id']
        read_only_fields = ['id']

    def to_representation(self, obj):

        data = super().to_representation(obj)

        # request = self.context['request']
        try:
            # import pdb;pdb.set_trace()
            if obj.usertype_from == 'PRIMARY':
                from_id = obj.request_from
                to_id = obj.request_to
                data['type'] = 'status_change_primary_to_secondary'
                data['request_from_name'] = FileUpload.objects.get(primary_user_id=int(from_id)).name
                data['request_to_name'] = Members.objects.get(secondary_user_id=int(to_id)).member_name
                data['family_name'] = FileUpload.objects.get(primary_user_id=int(from_id)).get_file_upload.first().name
                data['prayer_group_name'] = FileUpload.objects.get(primary_user_id=int(from_id)).get_file_upload_prayergroup.first().name
                data['from_phone_number'] = FileUpload.objects.get(primary_user_id=int(from_id)).phone_no_primary
                try:
                    if Members.objects.get(secondary_user_id=int(to_id)).phone_no_secondary_user : 
                        data['to_phone_number'] = Members.objects.get(secondary_user_id=int(to_id)).phone_no_secondary_user
                    else:
                        data['to_phone_number'] = None
                except:
                    data['to_phone_number'] = None
            elif(obj.usertype_from == 'SECONDARY'):
                from_id = obj.request_from
                to_id = obj.request_to
                data['type'] = 'status_change_after_beraevement'
                data['request_from_name'] = Members.objects.get(secondary_user_id=int(from_id)).member_name
                data['request_to_name'] = FileUpload.objects.get(primary_user_id=int(to_id)).name
                data['family_name'] = FileUpload.objects.get(primary_user_id=int(to_id)).get_file_upload.first().name
                data['prayer_group_name'] = FileUpload.objects.get(primary_user_id=int(to_id)).get_file_upload_prayergroup.first().name
                try:
                    if Members.objects.get(secondary_user_id=int(from_id)).phone_no_secondary_user : 
                        data['from_phone_number'] = Members.objects.get(secondary_user_id=int(from_id)).phone_no_secondary_user
                    else:
                        data['from_phone_number'] = None
                except:
                    data['from_phone_number'] = None

                try:
                    if FileUpload.objects.get(primary_user_id=int(to_id)).phone_no_primary : 
                        data['to_phone_number'] =FileUpload.objects.get(primary_user_id=int(to_id)).phone_no_primary
                    else:
                        data['to_phone_number'] = None
                except:
                    data['to_phone_number'] = None
        except:
            data['request_from_name'] = None

        data['rejected'] = obj.is_accepted
        data['date'] = obj.date
        try:
            data['date_format'] = tz.localtime(obj.date, pytz.timezone('Asia/Kolkata')).strftime("%d/%m/%Y, %H:%M:%S %p")
        except:
            data['date_format'] = obj.date.strftime("%d/%m/%Y, %H:%M:%S %p")
        try:
            if obj.status:
                data['status'] = obj.status
            else:
                data['status'] = 'Pending'
        except:
            data['status'] = 'Pending'

        return data
        return data


class NumberChangePrimarySerializer(serializers.ModelSerializer):
    class Meta:
        model = NumberChangePrimary
        fields = ['request_from_primary', 'number_from','number_to','id']
        read_only_fields = ['id']

    def to_representation(self, obj):
        data = super().to_representation(obj)
        request = self.context['request']
        request_from = obj.request_from_primary
        try:
            data['name'] = FileUpload.objects.get(primary_user_id=int(request_from)).name
        except:
            data['name'] = None
        try:
            data['type'] = 'number_change_primary'
        except:
            data['type'] = None

        data['rejected'] = obj.is_accepted
        data['date'] = obj.date
        try:
            data['date_format'] = tz.localtime(obj.date, pytz.timezone('Asia/Kolkata')).strftime("%d/%m/%Y, %H:%M:%S %p")
        except:
            data['date_format'] = obj.date.strftime("%d/%m/%Y, %H:%M:%S %p")
        try:
            if obj.status:
                data['status'] = obj.status
            else:
                data['status'] = 'Pending'
        except:
            data['status'] = 'Pending'
        return data


class AdminRequestSerializer(serializers.ModelSerializer):
    status_change = PrimaryToSecondarySerializer(many=True,read_only=True)

    class Meta:
        model = NumberChangePrimary
        fields = ['request_from_primary', 'number_from','number_to','id','status_change']
        read_only_fields = ['id'] 

    def to_representation(self, obj):
        data = super().to_representation(obj)
        request = self.context['request']
        request_from = obj.request_from_primary
        try:
            data['name'] = FileUpload.objects.get(primary_user_id=int(request_from)).name
        except:
            data['name'] = None
        try:
            data['family_name'] = FileUpload.objects.get(primary_user_id=int(request_from)).get_file_upload.first().name
        except:
            data['family_name'] = None

        try:
            data['prayer_group_name'] = FileUpload.objects.get(primary_user_id=int(request_from)).get_file_upload_prayergroup.first().name
        except:
            data['prayer_group_name'] = None

        try:
            data['type'] = 'number_change_primary'
        except:
            data['type'] = None

        try:
            user_obj = FileUpload.objects.get(primary_user_id=int(request_from))
            if user_obj.phone_no_primary == obj.number_from:
                data['number_type'] = 'PRIMARY NUMBER'
            elif user_obj.phone_no_secondary == obj.number_from:
                data['number_type'] = 'SECONDARY NUMBER'
            else:
                data['number_type'] = None  
        except:
            data['number_type'] = None  
              
        data['rejected'] = obj.is_accepted
        data['date'] = obj.date
        try:
            data['date_format'] = tz.localtime(obj.date, pytz.timezone('Asia/Kolkata')).strftime("%d/%m/%Y, %I:%M:%S %p")
        except:
            data['date_format'] = obj.date.strftime("%d/%m/%Y, %H:%M:%S %p")
        try:
            if obj.status:
                data['status'] = obj.status
            else:
                data['status'] = 'Pending'
        except:
            data['status'] = 'Pending'
        return data

#searching

class MembersSerializerPage(serializers.ModelSerializer):
    # phone_no_primary = serializers.SerializerMethodField()
    in_memory_date = serializers.SerializerMethodField()

    # family_

    class Meta:
        model = Members
        fields = ['image','dob','dom','blood_group','email','occupation','about','marital_status',\
        'in_memory','in_memory_date','relation','primary_user_id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # data['name'] = data.pop('member_name')
        data['user_type'] = 'SECONDARY'
        data['user_id'] = instance.secondary_user_id
        request = self.context['request']
        try:
            data['name'] = instance.member_name.title()
        except:
            data['name'] = None
        try:
            data['about'] = instance.about
        except:
            pass
        try :
            data['image'] = request.build_absolute_uri(instance.image.url)
        except:
            data['image'] = None
        try :
            data['address'] = ''
        except:
            data['address'] = None

        try:
            data['phone_no_primary'] = instance.phone_no_secondary_user
        except:
            data['phone_no_primary'] = None

        try:
            data['phone_no_secondary'] = instance.phone_no_secondary_user_secondary
        except:
            data['phone_no_secondary'] = None

        try:
            data['family_name'] = instance.primary_user_id.get_file_upload.first().name.title()
        except:
            data['family_name'] = ''
        try:
            data['active'] = instance.primary_user_id.get_file_upload.first().active
        except:
            data['active'] = ''
        try:
            data['family_id'] = instance.primary_user_id.get_file_upload.first().id
        except:
            data['family_id'] = ''
        try:
            data['primary_name'] = instance.primary_user_id.name.title()
        except:
            data['primary_name'] = ''
        return data



    def get_in_memory_date(self, obj):
        date = obj.in_memory_date
        if date:
            return date
        else:
            return None

    # def get_primary_name(self, obj):
    #     name = obj.primary_user_id.name
    #     if name:
    #         serializer = UserRetrieveSerializerPage(name,context=self.context)
    #         return name
    #     return None

    # def get_phone_no_primary(self, obj):
    #     primary_number = obj.primary_user_id.phone_no_primary
    #     if primary_number:
    #         serializer = UserRetrieveSerializerPage(primary_number)
    #         return primary_number
    #     return None

class PrimaryUserSerializerPage(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields =['name','image','address','phone_no_primary','phone_no_secondary','dob','dom','blood_group','email','occupation','about','marital_status',\
        'in_memory','in_memory_date','relation','primary_user_id']
        read_only_fields = ['primary_user_id']

    def to_representation(self, obj):

        data = super().to_representation(obj)

        request = self.context['request']

        if obj.get_file_upload.first():
            data['family_name'] = obj.get_file_upload.first().name.title()
        else:
            data['family_name'] = ''
        try:
            data['active'] = obj.get_file_upload.first().active
        except:
            data['active'] = ''
        try:
            data['family_id'] = obj.get_file_upload.first().id
        except:
            data['family_id'] = ''
        try:
            data['name'] = obj.name.title()
        except:
            pass
        try:
            data['primary_name'] = obj.name.title()
        except:
            pass   
        try:
            data['user_id'] = obj.primary_user_id
        except:
            pass
        if obj.image:
            try :
                data['image'] = request.build_absolute_uri(obj.image.url)
            except:
                data['image'] = None

        data['user_type'] = 'PRIMARY'

        return data

class UserMemorySerializer(serializers.Serializer):
    prayer_group = serializers.PrimaryKeyRelatedField(queryset=PrayerGroup.objects.all())
    family = serializers.PrimaryKeyRelatedField(queryset=Family.objects.all())
    name = serializers.CharField()
    # blood_group = serializers.CharField()
    dob = serializers.CharField(required=False,allow_blank=True)
    # email = serializers.EmailField()
    # primary_number = serializers.CharField()
    # secondary_number = serializers.CharField()
    # occupation = serializers.CharField()
    # marital_status = serializers.CharField()
    # marrige_date = serializers.CharField(allow_blank=True)
    member_type = serializers.CharField()
    member_status = serializers.ChoiceField(choices=['active', 'in_memory'])
    in_memory_date = serializers.DateTimeField()
    # about = serializers.CharField()

class ChangeRequestSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d/%m/%Y %I:%M %p", read_only=True)
    updated_at = serializers.DateTimeField(format="%d/%m/%Y %I:%M %p", read_only=True)

    class Meta:
        model = ChangeRequest
        fields = '__all__'

    def to_representation(self, obj):
        data = super().to_representation(obj)
        try:
            if obj.request_type == 'mobile':
                data['type'] = 'change_request_mobile'
                data['family_name'] = None
                data['primary_number'] = None
                data['secondary_number'] = None
            elif(obj.request_type == 'family'):
                if obj.user_type == 'primary':
                    prime_obj = FileUpload.objects.get(primary_user_id=int(obj.user_id))
                    data['family_name'] = prime_obj.get_file_upload.first().name
                    data['prayer_group_name'] = prime_obj.get_file_upload_prayergroup.first().name
                    data['primary_number'] = prime_obj.phone_no_primary
                    data['mobile_number'] = prime_obj.phone_no_primary
                    data['user_name'] = prime_obj.name
                    data['mobile_number_head_of_family'] = prime_obj.phone_no_primary
                elif obj.user_type == 'secondary':
                    obj_sec = Members.objects.get(secondary_user_id=int(obj.user_id))
                    prime_obj = FileUpload.objects.get(primary_user_id=obj_sec.primary_user_id.primary_user_id)
                    data['family_name'] = prime_obj.get_file_upload.first().name
                    data['prayer_group_name'] = prime_obj.get_file_upload_prayergroup.first().name
                    data['primary_number'] = obj_sec.phone_no_secondary_user
                    data['mobile_number'] = obj_sec.phone_no_secondary_user
                    data['user_name'] = obj_sec.member_name
                    data['mobile_number_head_of_family'] = prime_obj.phone_no_primary
                else:
                    data['family_name'] = None
                    data['primary_number'] = None
                    data['secondary_number'] = None
                data['type'] = 'change_request_family'
            else:
                pass
            try:
                data['date'] = obj.created_at
                data['date_format'] = tz.localtime(obj.created_at, pytz.timezone('Asia/Kolkata')).strftime("%d/%m/%Y, %H:%M:%S %p")
            except:
                data['date_format'] = obj.date.strftime("%d/%m/%Y, %H:%M:%S %p")
                data['date'] = obj.created_at
        except:
            try:
                data['date'] = obj.created_at
                data['date_format'] = tz.localtime(obj.created_at, pytz.timezone('Asia/Kolkata')).strftime("%d/%m/%Y, %H:%M:%S %p")
            except:
                data['date_format'] = obj.date.strftime("%d/%m/%Y, %H:%M:%S %p")
                data['date'] = obj.created_at
        return data
    def create(self, validated_data):
        change_request = ChangeRequest(**validated_data)
        change_request.save()
        admin_profiles = AdminProfile.objects.all()

        try:
            request = self.context['request']
            image= ""
        except:
            image = ""
        try:
            for admin_profile in admin_profiles:
                content = {'title':'Request','message':{"data":{"title":"Request","body":"You have received a new request","notificationType":"request","backgroundImage":image,"text_type":"long"},\
                "notification":{"alert":"This is a FCM notification","title":"Request","body":"You have received a new request","sound":"default","backgroundImage":image,"backgroundImageTextColour":"#FFFFFF","image":image,"click_action":"request"}} } 

                content_ios = {'message':{"aps":{"alert":{"title":"Request","subtitle":"","body":"You have received a new request"},"sound":"default","category":"request","badge":1,"mutable-content":1},"media-url":image}}
                resp = fcm_messaging_to_user(admin_profile.user,content)
                resp1 = apns_messaging_to_user(admin_profile.user,content_ios)
        except:
            pass
        return change_request

class VicarsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurchVicars
        fields = '__all__'