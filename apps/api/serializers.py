from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
import requests
from apps.church.models import UserProfile, ChurchDetails, FileUpload, OtpModels, \
    OtpVerify, PrayerGroup, Notification, Family, Members, Notice, NoticeBereavement, \
    UnapprovedMember, NoticeReadPrimary, NoticeReadSecondary, NoticeReadAdmin, ViewRequestNumber, PrivacyPolicy, \
    PhoneVersion, Images
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
from apps.api.models import AdminProfile
from django.utils import timezone as tz


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
        fields = ['name','members_length','image','id']

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
        data = super().to_representation(instance)

        data['user_type'] = 'PRIMARY'

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

    class Meta:
        model = OtpVerify
        fields = ['otp','user_type']


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

    def get_in_memory_date(self, obj):
        date = obj.in_memory_date
        if date:
            return date
        else:
            return None

    def get_primary_name(self, obj):
        name = obj.primary_user_id.name
        if name:
            serializer = UserRetrieveSerializer(name)
            return name
        return None

    def get_phone_no_primary(self, obj):
        primary_number = obj.primary_user_id.phone_no_primary
        if primary_number:
            serializer = UserRetrieveSerializer(primary_number)
            return primary_number
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['user_type'] = 'SECONDARY'

        return data

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

        # body="You have received a new notice"
        notifications=Notification.objects.create(created_time=tz.now(),message=body)
        primary_members=FileUpload.objects.all()
        secondary_members=Members.objects.all()
        for primary_member in primary_members:
            NoticeReadPrimary.objects.create(notification=notifications,user_to=primary_member,is_read=False)
        for secondary_member in secondary_members:
            NoticeReadSecondary.objects.create(notification=notifications,user_to=secondary_member,is_read=False)
        
        return notice

    def update(self, request, *args, **kwargs):

        instance = super().update(instance, validated_data)
        instance.save()
        
        # body="A notice has been modified"
        body= {"message":"A notice has been modified",
                            "type":"notice",
                            "id":str(instance.id)
            }
        notifications=Notification.objects.create(created_time=tz.now(),message=body)
        primary_members=FileUpload.objects.all()
        secondary_members=Members.objects.all()
        for primary_member in primary_members:
            NoticeReadPrimary.objects.create(notification=notifications,user_to=primary_member,is_read=False)
        for secondary_member in secondary_members:
            NoticeReadSecondary.objects.create(notification=notifications,user_to=secondary_member,is_read=False)
        
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
        return data


class NoticeBereavementSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d/%m/%Y %I:%M %p", read_only=True)
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
        return data


class UserDetailsRetrieveSerializer(serializers.ModelSerializer):
    in_memory_date = serializers.SerializerMethodField()
    # family_name = serializers.SerializerMethodField()
    # family_description = serializers.SerializerMethodField()
    class Meta:
        model = FileUpload
        fields = ['primary_user_id','image','name','address','phone_no_primary','phone_no_secondary','dob','dom','blood_group','email','in_memory','in_memory_date','occupation','about']

    def get_in_memory_date(self, obj):
        date = obj.in_memory_date
        if date:
            return date
        else:
            return None

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

        data['user_type'] = 'SECONDARY'

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

        notification = Notification.objects.create(
            created_by_primary=primary_user, 
            message="User %s added a family member %s. Verify and approve to reflect changes"%(primary_user, unapproved_member)
        )

        admin_profiles = UserProfile.objects.all()

        for admin_profile in admin_profiles:
            NoticeReadAdmin.objects.create(notification=notification, user_to=admin_profile)

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

        admin_profiles = UserProfile.objects.all()
        
        for admin_profile in admin_profiles:
            NoticeReadAdmin.objects.create(notification=notification, user_to=admin_profile)

        return instance

    def to_representation(self, obj):

        data = super().to_representation(obj)

        data['rejected'] = obj.rejected
        data['primary_user_id'] = obj.primary_user_id.primary_user_id
        data['edit_user'] = obj.edit_user

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
                data['family_name'] = obj.primary_user_id.get_file_upload.first().name
            except:
                data['family_name'] = ''

        else:
            data['family_name' ] = ''

        if obj.image:
            try :
                data['image'] = request.build_absolute_uri(instance.image.url)
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
            data['family_name'] = obj.get_file_upload.first().name
        else:
            data['family_name'] = ''

        if obj.image:
            try :
                data['image'] = request.build_absolute_uri(instance.image.url)
            except:
                data['image'] = None

        data['user_type'] = 'primary'

        return data


class UserByadminSerializer(serializers.Serializer):
    prayer_group = serializers.PrimaryKeyRelatedField(queryset=PrayerGroup.objects.all())
    family = serializers.PrimaryKeyRelatedField(queryset=Family.objects.all())
    name = serializers.CharField()
    blood_group = serializers.CharField()
    dob = serializers.CharField()
    email = serializers.EmailField()
    primary_number = serializers.CharField()
    secondary_number = serializers.CharField()
    occupation = serializers.CharField()
    marital_status = serializers.CharField()
    marrige_date = serializers.CharField(allow_blank=True)
    member_type = serializers.CharField()
    member_status = serializers.ChoiceField(choices=['active', 'in_memory'])
    about = serializers.CharField()


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