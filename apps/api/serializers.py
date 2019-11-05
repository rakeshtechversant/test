from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
import requests
from apps.church.models import UserProfile, ChurchDetails, FileUpload, OtpModels, \
    OtpVerify, PrayerGroup, Notification, Family, Members, Notice, NoticeBereavement, \
    UnapprovedMember
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
    class Meta:
        model = Family
        fields = ['name','members_length']

class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['primary_user_id','image','name','address','phone_no_primary','phone_no_secondary','dob','dom','blood_group','email']


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
                    'title': image.title,
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

    class Meta:
        model = Members
        fields = ['phone_no_primary','primary_name','secondary_user_id','member_name','relation','dob','dom','image','phone_no_secondary_user','primary_user_id']

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

        return data


class NoticeBereavementSerializer(serializers.ModelSerializer):
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

        return data


class UserDetailsRetrieveSerializer(serializers.ModelSerializer):
    in_memory_date = serializers.SerializerMethodField()
    family_name = serializers.SerializerMethodField()
    family_description = serializers.SerializerMethodField()
    class Meta:
        model = FileUpload
        fields = ['primary_user_id','image','name','address','phone_no_primary','phone_no_secondary','dob','dom','blood_group','email','in_memory','in_memory_date','occupation','about','family_name','family_description']

    def get_in_memory_date(self, obj):
        date = obj.in_memory_date
        if date:
            return date
        else:
            return None

    def get_family_name(self, obj):
        try:
            name = obj.get_file_upload.get().name
        except:
            name = None
        return name

    def get_family_description(self, obj):
        try:
            about = obj.get_file_upload.get().about
        except:
            about = None
        return about

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
        name = obj.primary_user_id.name
        if name:
            serializer = UserDetailsRetrieveSerializer(name)
            return name
        return None

    def get_phone_no_primary(self, obj):
        primary_number = obj.primary_user_id.phone_no_primary
        if primary_number:
            serializer = UserDetailsRetrieveSerializer(primary_number)
            return primary_number
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['user_type'] = 'SECONDARY'

        return data


class UnapprovedMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = UnapprovedMember
        exclude = ['primary_user_id', 'rejected']

    def create(self, validated_data):

        created_by = self.context['request'].user

        primary_user = FileUpload.objects.get(phone_no_primary=created_by.username)

        unapproved_member = UnapprovedMember(**validated_data)
        unapproved_member.primary_user_id = primary_user
        unapproved_member.save()

        return unapproved_member

    def update(self, instance, validated_data):

        instance = super().update(instance, validated_data)
        instance.rejected = False
        instance.save()

        return instance

    def to_representation(self, obj):

        data = super().to_representation(obj)

        data['rejected'] = obj.rejected
        data['primary_user_id'] = obj.primary_user_id.primary_user_id

        return data

