from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
import requests
from apps.church.models import UserProfile,ChurchDetails,FileUpload,OtpModels,OtpVerify,PrayerGroup,Notification,Family
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
class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','password','email']



class UserRegistrationMobileSerializer(serializers.ModelSerializer):
    class Meta:
        model=OtpModels
        fields = ['mobile_number','user_type']

    # def validate(self, data):
    #     user_count=0
    #     mobile_number = data.get("mobile_number", None)
    #     user_type = data.get("user_type", None)
    #     if user_type == 'PRIMARY' or 'SECONDARY' or 'CHURCH':
    #
    #         for userprofile in FileUpload.objects.all():
    #             if userprofile.mobile_number == mobile_number:
    #                 user_count=user_count+1
    #                 if not mobile_number:
    #                     raise serializers.ValidationError("This field is required")
    #                 if UserProfile.objects.filter(mobile_number = mobile_number).exists():
    #                     raise serializers.ValidationError("This number is already taken")
    #                 if mobile_number:
    #                     otp_number = get_random_string(length=6, allowed_chars='1234567890')
    #                     try:
    #                         OtpModels.objects.filter(mobile_number=mobile_number).delete()
    #                     except:
    #                         pass
    #                     OtpModels.objects.create(mobile_number=mobile_number, otp=otp_number)
    #                     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    #                     message = client.messages.create(to='+91' + mobile_number, from_='+15036837180',body=otp_number)
    #
    #             else:
    #                 if user_count ==0:
    #                     raise serializers.ValidationError("We couldn't find your profile in database,Please contact service providers")
    #
    #     else:
    #         raise serializers.ValidationError("Invalid usertype,Please select again")
    #
    #     return data


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
        fields = ['name']

class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user','family','dob','occupation','about','profile_image','mobile_number','date_of_marriage']


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user_id','family','dob','occupation','about','profile_image','mobile_number','date_of_marriage']




class ChurchAddUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurchDetails
        fields = ['church_name','description','image','cover_image','address']


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['user','first_name','last_name']


class OTPVeifySerializer(serializers.ModelSerializer):
    class Meta:
        model = OtpVerify
        fields = ['otp']


class SecondaryaddSerializer(serializers.ModelSerializer):
    secondary_user = serializers.PrimaryKeyRelatedField(queryset=FileUpload.objects.all(), many=True,read_only=False)

    class Meta:
        model = UserProfile
        fields = ['secondary_user']
        read_only_fields = ('user',)

    def update(self, instance, validated_data):
        if instance.is_primary == True:
            for secondary_user in validated_data['secondary_user']:
                sec_user = FileUpload.objects.get(id=secondary_user.id)
                instance.secondary_user.add(sec_user)
            Notification.objects.create(user=instance,is_user_add_new_member=True,created_time=datetime.strptime('2018-02-16 11:00 AM', "%Y-%m-%d %I:%M %p"))
        else:
           raise serializers.ValidationError("You don't have permission to add family members")
        # seconday_user =  data.get('sec_user')
        return instance

class PrayerGroupAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrayerGroup
        fields = ['name']

class PrayerGroupAddMembersSerializer(serializers.ModelSerializer):
    user_profile = serializers.PrimaryKeyRelatedField(queryset=FileUpload.objects.all(), many=True,read_only=False)
    class Meta:
        model = PrayerGroup
        fields = ['user_profile']
        read_only_fields = ('name',)

    def update(self, instance, validated_data):
        # if instance.is_staff == True:
        for user_profiles in validated_data['user_profile']:
            member_user = FileUpload.objects.get(id=user_profiles.id)
            instance.user_profile.add(member_user)
        # else:
        #    raise serializers.ValidationError("You don't have permission to add family members")
        # seconday_user =  data.get('sec_user')
        return instance
