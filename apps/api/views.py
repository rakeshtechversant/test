from django.shortcuts import render
from django.contrib.auth import password_validation, authenticate
from django.db.models import Q
from django.http import Http404
from operator import itemgetter
# Create your views here.
import ast
import json
from rest_framework import mixins
from rest_framework import exceptions
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet,ViewSet
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView, \
    DestroyAPIView, CreateAPIView, UpdateAPIView
from rest_framework import status
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import parsers
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
import requests
from apps.api.permissions import IsOwnerOrReadOnly, IsPrimaryUserOrReadOnly, AdminPermission
from apps.api.utils import MultipartJsonParser
from apps.api.serializers import ChurchHistorySerializer, ChurchImagesSerializer, LoginSerializer, FamilyListSerializer, \
    UserRegistrationMobileSerializer, \
    PrayerGroupAddMembersSerializer, PrayerGroupAddSerializer, UserListSerializer, UserRetrieveSerializer, \
    UserCreateSerializer, ChurchVicarSerializer, FileUploadSerializer, OTPVeifySerializer, SecondaryaddSerializer, \
    MembersSerializer, NoticeSerializer, AdminProfileSerializer, PrimaryUserProfileSerializer, MemberProfileSerializer, \
    NoticeBereavementSerializer, \
    UserDetailsRetrieveSerializer, MembersDetailsSerializer, UnapprovedMemberSerializer, MemberSerializer, \
    PrimaryUserSerializer, \
    UserByadminSerializer, FamilyByadminSerializer, PrimaryNotificationSerializer, SecondaryNotificationSerializer, \
    ViewRequestNumberSerializer, RequestAcceptNumberSerializer, AdminNotificationSerializer, PhoneVersionSerializer, \
    GalleryImagesSerializer, FamilyDetailSerializer, FamilyEditSerializer, GalleryImagesCreateSerializer, \
    OTPVeifySerializerUserId, CommonUserSerializer, MemberNumberSerializer, PrimaryToSecondarySerializer, NumberChangePrimarySerializer ,\
    AdminRequestSerializer, PrimaryUserSerializerPage, MembersSerializerPage, UserMemorySerializer, UserByMembersSerializer
from apps.church.models import Members, Family, UserProfile, ChurchDetails, FileUpload, OtpModels, \
    PrayerGroup, Notification, Notice, NoticeBereavement, UnapprovedMember, NoticeReadPrimary, NoticeReadSecondary, \
    ViewRequestNumber, NoticeReadAdmin, PrivacyPolicy, PhoneVersion, Images, PrimaryToSecondary, NumberChangePrimary

from apps.api.models import AdminProfile
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, \
HTTP_404_NOT_FOUND
from django.utils.crypto import get_random_string
from twilio.rest import Client
from church_project import settings
from datetime import datetime, timezone
from django.utils import timezone as tz

from django.contrib.auth.models import User
from django.views.generic import TemplateView
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
import csv
from push_notifications.models import APNSDevice, GCMDevice

def fcm_messaging_to_all(content):
    try: 
        device = GCMDevice.objects.filter(active=True).exclude(user__is_superuser=True)
        message = content['message']['data']['body']
        title = content['message']['data']['title']
        status = device.send_message(message,title=title, extra=content['message'])
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
        device_ios.send_message(message={"title" : title_ios, "body" : message_ios}, extra=content_ios['message'])
        return status 
    except Exception as exp:
        print("notify-ios",exp)
        return str(exp) 

def apns_messaging_to_user(user,content_ios):
    try: 
        device_ios = APNSDevice.objects.filter(user=user,active=True)
        message_ios = content_ios['message']['aps']['alert']['body']
        title_ios = content_ios['message']['aps']['alert']['title']
        device_ios.send_message(message={"title" : title_ios, "body" : message_ios}, extra=content_ios['message'])
        return status 
    except Exception as exp:
        print("notify-ios",exp)
        return str(exp)

class UserLoginMobileView(APIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserRegistrationMobileSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        mobile_number = request.data['mobile_number']
        user_type  = request.data['user_type']
        user_id  = request.data['user_id']
        try:
            superusers = AdminProfile.objects.filter(user__is_superuser=True).first()
            admin_phonenumber = superusers.mobile_number
        except:
            admin_phonenumber = ''
        if not mobile_number:
            return Response({'message': 'Mobile field should not be blank', 'success': False},
                            status=HTTP_400_BAD_REQUEST)
        else:
            # import pdb;pdb.set_trace()
            try:
                user_profile = Members.objects.get(secondary_user_id=user_id)
                if user_type == 'SECONDARY' and user_id :
                    if user_profile.primary_user_id.phone_no_primary == mobile_number or user_profile.primary_user_id.phone_no_secondary == mobile_number:
                        if(user_profile.primary_user_id.phone_no_secondary == None):
                            data = {
                                'admin_mobile_number' : admin_phonenumber,
                            }
                            return Response({'success': False, 'message': 'Please contact admin','user_details': data},
                            status=HTTP_404_NOT_FOUND)
                        else:
                            user,created=User.objects.get_or_create(username=mobile_number)
                            token, created = Token.objects.get_or_create(user=user)
                            data = {
                                'mobile': mobile_number,
                                'user_type': 'SECONDARY',
                                'name': user_profile.member_name,
                                'token':token.key,
                                'user_id':user_profile.secondary_user_id
                            }
                            otp_number = get_random_string(length=6, allowed_chars='1234567890')
                            try:
                                OtpModels.objects.filter(mobile_number=mobile_number).delete()
                            except:
                                pass
                            OtpModels.objects.create(mobile_number=mobile_number, otp=otp_number)
                            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                            # message = client.messages.create(to='+91' + mobile_number, from_='+15036837180',body=otp_number)
                            message = "OTP for login is %s" % (otp_number,)
                            requests.get(
                                "http://unifiedbuzz.com/api/insms/format/json/?mobile=" + mobile_number + "&text=" + message +
                                "&flash=0&type=1&sender=MARCHR",
                                headers={"X-API-Key": "918e0674e62e01ec16ddba9a0cea447b"})
                            return Response({'success': True, 'message': 'OTP Sent Successfully', 'user_details': data},
                                            status=HTTP_200_OK)
                                           
                    else:
                        pass
            except:
                pass
            if AdminProfile.objects.filter(mobile_number=mobile_number):
                admin_profile = AdminProfile.objects.get(mobile_number=mobile_number)
                if mobile_number == admin_profile.mobile_number:
                    user=User.objects.get(username=admin_profile.user)
                    token, created = Token.objects.get_or_create(user=user)
                    data = {
                        'mobile': admin_profile.mobile_number,
                        'user_type': 'ADMIN',
                        'name': 'admin',
                        'token':token.key,
                        'user_id':admin_profile.id
                    }
                    if mobile_number == '9995507393' :
                        otp_number = '99956'
                    elif mobile_number == '9999988888':
                        otp_number = '99955'
                    else:
                        otp_number = get_random_string(length=6, allowed_chars='1234567890')
                    try:
                        OtpModels.objects.filter(mobile_number=mobile_number).delete()
                    except:
                        pass

                    OtpModels.objects.create(mobile_number=mobile_number, otp=otp_number)
                    # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                    # message = client.messages.create(to='+91' + mobile_number, from_='+15036837180',body=otp_number)

                    message = "OTP for login is %s" % (otp_number,)
                    requests.get(
                        "http://unifiedbuzz.com/api/insms/format/json/?mobile=" + mobile_number + "&text=" + message +
                        "&flash=0&type=1&sender=MARCHR",
                        headers={"X-API-Key": "918e0674e62e01ec16ddba9a0cea447b"})
                    return Response({'success': True, 'message': 'OTP Sent Successfully', 'user_details': data},
                                    status=HTTP_200_OK)
                else:
                    pass
            else:
                if FileUpload.objects.filter(phone_no_primary=mobile_number):
                    user_profiles = FileUpload.objects.filter(phone_no_primary=mobile_number)
                    for user_profile in user_profiles:
                        if mobile_number == user_profile.phone_no_primary:
                            user,created=User.objects.get_or_create(username=mobile_number)
                            token, created = Token.objects.get_or_create(user=user)
                            data = {
                                'mobile': user_profile.phone_no_primary,
                                'user_type': 'PRIMARY',
                                'name': user_profile.name,
                                'token':token.key,
                                'user_id':user_profile.primary_user_id
                            }
                            otp_number = get_random_string(length=6, allowed_chars='1234567890')
                            try:
                                OtpModels.objects.filter(mobile_number=mobile_number).delete()
                            except:
                                pass
                            OtpModels.objects.create(mobile_number=mobile_number, otp=otp_number)
                            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                            # message = client.messages.create(to='+91' + mobile_number, from_='+15036837180',body=otp_number)
                            message = "OTP for login is %s" % (otp_number,)
                            requests.get(
                                "http://unifiedbuzz.com/api/insms/format/json/?mobile=" + mobile_number + "&text=" + message +
                                "&flash=0&type=1&sender=MARCHR",
                                headers={"X-API-Key": "918e0674e62e01ec16ddba9a0cea447b"})
                            return Response({'success': True, 'message': 'OTP Sent Successfully', 'user_details': data},
                                            status=HTTP_200_OK)
                        else:
                            data = {}
                            return Response({'message': 'You are not in primary list', 'success': False},
                                            status=HTTP_400_BAD_REQUEST)

                elif FileUpload.objects.filter(phone_no_secondary=mobile_number):
                    user_profiles = FileUpload.objects.filter(phone_no_secondary=mobile_number)
                    for user_profile in user_profiles:
                        if mobile_number == user_profile.phone_no_secondary:
                            user,created=User.objects.get_or_create(username=mobile_number)
                            token, created = Token.objects.get_or_create(user=user)
                            data = {
                                'mobile': user_profile.phone_no_primary,
                                'user_type': 'PRIMARY',
                                'name': user_profile.name,
                                'token':token.key,
                                'user_id':user_profile.primary_user_id
                            }
                            otp_number = get_random_string(length=6, allowed_chars='1234567890')
                            try:
                                OtpModels.objects.filter(mobile_number=user_profile.phone_no_primary).delete()
                            except:
                                pass
                            OtpModels.objects.create(mobile_number=user_profile.phone_no_primary, otp=otp_number)
                            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                            # message = client.messages.create(to='+91' + mobile_number, from_='+15036837180',body=otp_number)
                            message = "OTP for login is %s" % (otp_number,)
                            requests.get(
                                "http://unifiedbuzz.com/api/insms/format/json/?mobile=" + user_profile.phone_no_primary + "&text=" + message +
                                "&flash=0&type=1&sender=MARCHR",
                                headers={"X-API-Key": "918e0674e62e01ec16ddba9a0cea447b"})
                            return Response({'success': True, 'message': 'OTP Sent Successfully', 'user_details': data},
                                            status=HTTP_200_OK)
                        else:
                            data = {}
                            return Response({'message': 'You are not in primary list', 'success': False},
                                            status=HTTP_400_BAD_REQUEST)

                elif Members.objects.filter(phone_no_secondary_user=mobile_number):
                    user_details = Members.objects.filter(phone_no_secondary_user=mobile_number)
                    for user_profile in user_details:
                        user,created=User.objects.get_or_create(username=mobile_number)
                        token, created = Token.objects.get_or_create(user=user)
                        if mobile_number == user_profile.phone_no_secondary_user:
                            data = {
                                'mobile': user_profile.phone_no_secondary_user,
                                'user_type': 'SECONDARY',
                                'name': user_profile.member_name,
                                'token':token.key,
                                'primary_user_name': user_profile.primary_user_id.name,
                                'primary_user_id': user_profile.primary_user_id.primary_user_id,
                                'phone_no_primary' : user_profile.primary_user_id.phone_no_primary,
                                'user_id':user_profile.secondary_user_id
                            }

                            otp_number = get_random_string(length=6, allowed_chars='1234567890')

                            try:
                                OtpModels.objects.filter(mobile_number=user_profile.phone_no_secondary_user).delete()
                            except:
                                pass

                            OtpModels.objects.create(mobile_number=user_profile.phone_no_secondary_user, otp=otp_number)
                            
                            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                            # message = client.messages.create(to='+91' + mobile_number, from_='+15036837180',body=otp_number)
                            message = "OTP for login is %s" % (otp_number,)
                            requests.get(
                                "http://unifiedbuzz.com/api/insms/format/json/?mobile=" + user_profile.phone_no_secondary_user + "&text=" + message +
                                "&flash=0&type=1&sender=MARCHR",
                                headers={"X-API-Key": "918e0674e62e01ec16ddba9a0cea447b"})

                            return Response({'success': True, 'message': 'OTP Sent Successfully', 'user_details': data},
                                            status=HTTP_200_OK)
                        else:
                            data = {}
                            return Response({'message': 'You are not in secondary list', 'success': False},
                                            status=HTTP_400_BAD_REQUEST)



                else:
                    data = {
                        'mobile': mobile_number,
                    }
                    return Response({
                                        'message': 'You are not in primary list,go to next section for update your number as secondary user',
                                        'success': False, 'user_details': data}, status=HTTP_400_BAD_REQUEST)

class UserLoginMobileWithOutOtpView(APIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserRegistrationMobileSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        mobile_number = request.data['mobile_number']
        user_type  = request.data['user_type']
        user_id  = request.data['user_id']
        try:
            superusers = AdminProfile.objects.filter(user__is_superuser=True).first()
            admin_phonenumber = superusers.mobile_number
        except:
            admin_phonenumber = ''
        if not mobile_number:
            return Response({'message': 'Mobile field should not be blank', 'success': False},
                            status=HTTP_400_BAD_REQUEST)
        else:
            # import pdb;pdb.set_trace()
            try:
                user_profile = Members.objects.get(secondary_user_id=user_id)
                if user_profile.primary_user_id.get_file_upload.first().members_length == 1 :
                    return Response({'message': 'Your family is in inactive state.Please contact admin', 'success': False},
                                status=HTTP_400_BAD_REQUEST)
                if user_type == 'SECONDARY' and user_id :

                    if user_profile.primary_user_id.phone_no_primary == mobile_number or user_profile.primary_user_id.phone_no_secondary == mobile_number:
                        if(user_profile.primary_user_id.phone_no_secondary == None):
                            data = {
                                'admin_mobile_number' : admin_phonenumber,
                            }
                            return Response({'success': False, 'message': 'Please contact admin','user_details': data},
                            status=HTTP_404_NOT_FOUND)
                        else:
                            user,created=User.objects.get_or_create(username=mobile_number)
                            token, created = Token.objects.get_or_create(user=user)
                            data = {
                                'mobile': mobile_number,
                                'user_type': 'SECONDARY',
                                'name': user_profile.member_name,
                                'token':token.key,
                                'user_id':user_profile.secondary_user_id
                            }
                            # otp_number = get_random_string(length=6, allowed_chars='1234567890')
                            # try:
                            #     OtpModels.objects.filter(mobile_number=mobile_number).delete()
                            # except:
                            #     pass
                            # OtpModels.objects.create(mobile_number=mobile_number, otp=otp_number)
                            # # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                            # # message = client.messages.create(to='+91' + mobile_number, from_='+15036837180',body=otp_number)
                            # message = "OTP for login is %s" % (otp_number,)
                            # requests.get(
                            #     "http://unifiedbuzz.com/api/insms/format/json/?mobile=" + mobile_number + "&text=" + message +
                            #     "&flash=0&type=1&sender=MARCHR",
                            #     headers={"X-API-Key": "918e0674e62e01ec16ddba9a0cea447b"})
                            return Response({'success': True, 'message': 'OTP Sent Successfully', 'user_details': data},
                                            status=HTTP_200_OK)
                                           
                    else:
                        pass
            except:
                pass
            if AdminProfile.objects.filter(mobile_number=mobile_number):
                admin_profile = AdminProfile.objects.get(mobile_number=mobile_number)
                if mobile_number == admin_profile.mobile_number:
                    user=User.objects.get(username=admin_profile.user)
                    token, created = Token.objects.get_or_create(user=user)
                    data = {
                        'mobile': admin_profile.mobile_number,
                        'user_type': 'ADMIN',
                        'name': 'admin',
                        'token':token.key,
                        'user_id':admin_profile.id
                    }

                    return Response({'success': True, 'message': 'Success Response', 'user_details': data},
                                    status=HTTP_200_OK)
                else:
                    pass
            else:
                if FileUpload.objects.filter(phone_no_primary=mobile_number):
                    user_profiles = FileUpload.objects.filter(phone_no_primary=mobile_number)
                    for user_profile in user_profiles:
                        if mobile_number == user_profile.phone_no_primary:
                            if user_profile.get_file_upload.first().members_length == 1 :
                                return Response({'message': 'Your family is in inactive state.Please contact admin', 'success': False},
                                            status=HTTP_400_BAD_REQUEST)
                            user,created=User.objects.get_or_create(username=mobile_number)
                            token, created = Token.objects.get_or_create(user=user)
                            data = {
                                'mobile': user_profile.phone_no_primary,
                                'user_type': 'PRIMARY',
                                'name': user_profile.name,
                                'prayer_group_name':user_profile.get_file_upload_prayergroup.first().name ,
                                'family_name':user_profile.get_file_upload.first().name ,
                                'prayer_group_id':user_profile.get_file_upload_prayergroup.first().id ,
                                'family_name_id':user_profile.get_file_upload.first().id ,
                                'token':token.key,
                                'user_id':user_profile.primary_user_id
                            }

                            return Response({'success': True, 'message': 'Success Response', 'user_details': data},
                                            status=HTTP_200_OK)
                        else:
                            data = {}
                            return Response({'message': 'Something went wrong', 'success': False},
                                            status=HTTP_400_BAD_REQUEST)

                elif FileUpload.objects.filter(phone_no_secondary=mobile_number):
                    user_profiles = FileUpload.objects.filter(phone_no_secondary=mobile_number)
                    for user_profile in user_profiles:
                        if mobile_number == user_profile.phone_no_secondary:
                            if user_profile.get_file_upload.first().members_length == 1 :
                                return Response({'message': 'Your family is in inactive state.Please contact admin', 'success': False},
                                            status=HTTP_400_BAD_REQUEST)
                            user,created=User.objects.get_or_create(username=mobile_number)
                            token, created = Token.objects.get_or_create(user=user)
                            data = {
                                'mobile': user_profile.phone_no_primary,
                                'user_type': 'PRIMARY',
                                'name': user_profile.name,
                                'prayer_group_name':user_profile.get_file_upload_prayergroup.first().name ,
                                'family_name':user_profile.get_file_upload.first().name ,
                                'prayer_group_id':user_profile.get_file_upload_prayergroup.first().id ,
                                'family_name_id':user_profile.get_file_upload.first().id ,
                                'token':token.key,
                                'user_id':user_profile.primary_user_id
                            }

                            return Response({'success': True, 'message': 'Success Response', 'user_details': data},
                                            status=HTTP_200_OK)
                        else:
                            data = {}
                            return Response({'message': 'Something went wrong', 'success': False},
                                            status=HTTP_400_BAD_REQUEST)

                elif Members.objects.filter(phone_no_secondary_user=mobile_number):
                    user_details = Members.objects.filter(phone_no_secondary_user=mobile_number)
                    for user_profile in user_details:
                        if user_profile.primary_user_id.get_file_upload.first().members_length == 1 :
                            return Response({'message': 'Your family is in inactive state.Please contact admin', 'success': False},
                                        status=HTTP_400_BAD_REQUEST)
                        user,created=User.objects.get_or_create(username=mobile_number)
                        token, created = Token.objects.get_or_create(user=user)
                        if mobile_number == user_profile.phone_no_secondary_user:
                            data = {
                                'mobile': user_profile.phone_no_secondary_user,
                                'user_type': 'SECONDARY',
                                'name': user_profile.member_name,
                                'prayer_group_name':user_profile.primary_user_id.get_file_upload_prayergroup.first().name ,
                                'family_name':user_profile.primary_user_id.get_file_upload.first().name ,
                                'prayer_group_id':user_profile.primary_user_id.get_file_upload_prayergroup.first().id ,
                                'family_name_id':user_profile.primary_user_id.get_file_upload.first().id ,
                                'token':token.key,
                                'primary_user_name': user_profile.primary_user_id.name,
                                'primary_user_id': user_profile.primary_user_id.primary_user_id,
                                'phone_no_primary' : user_profile.primary_user_id.phone_no_primary,
                                'user_id':user_profile.secondary_user_id
                            }


                            return Response({'success': True, 'message': 'Success Response', 'user_details': data},
                                            status=HTTP_200_OK)
                        else:
                            data = {}
                            return Response({'message': 'Something went wrong', 'success': False},
                                            status=HTTP_400_BAD_REQUEST)
                else:
                    data = {
                        'mobile': mobile_number,
                    }
                    return Response({
                                        'message': 'You are not in primary list,go to next section for update your number as secondary user',
                                        'success': False, 'user_details': data}, status=HTTP_400_BAD_REQUEST)

class OtpVerifyViewSet(CreateAPIView):
    queryset = OtpModels.objects.all()
    serializer_class = OTPVeifySerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data.get("otp", None)
        user_type = serializer.validated_data.get("user_type", None)
        try:
            otp_obj = OtpModels.objects.get(otp=otp)
            if (datetime.now(timezone.utc) - otp_obj.created_time).total_seconds() >= 1800:
                otp_obj.is_expired = True
                otp_obj.save()
                return Response({'success': False, 'message': 'Otp Expired'}, status=HTTP_400_BAD_REQUEST)
            if otp_obj.is_expired:
                return Response({'success': False, 'message': 'Otp Already Used'}, status=HTTP_400_BAD_REQUEST)
        except:
            return Response({'success': False, 'message': 'Invalid Otp'}, status=HTTP_400_BAD_REQUEST)
        else:
            if otp_obj:
                otp_obj.is_expired = True
                otp_obj.save()
            else:
                pass

            if user_type == "ADMIN":
                try:
                    admin = AdminProfile.objects.get(mobile_number=otp_obj.mobile_number)
                    user = admin.user
                    data = {
                        'mobile': admin.mobile_number,
                        'user_type': 'ADMIN',
                        'name': 'Admin',
                    }
                except AdminProfile.DoesNotExist:
                    return Response({'success': False, 'message': 'Admin account does not exist'}, status=HTTP_404_NOT_FOUND)

            elif user_type == "PRIMARY":
                try:
                    user_profile = FileUpload.objects.get(Q(phone_no_secondary=otp_obj.mobile_number) | Q(phone_no_primary=otp_obj.mobile_number))
                    user = otp_obj.mobile_number
                    mobile = user_profile.phone_no_primary if user_profile.phone_no_primary else user_profile.phone_no_secondary
                    data = {
                        'mobile': mobile,
                        'user_type': 'PRIMARY',
                        'name': user_profile.name,
                        'primary_user_id': user_profile.primary_user_id
                    }
                except FileUpload.DoesNotExist:
                    return Response({'success': False, 'message': 'Primary account does not exist'}, status=HTTP_404_NOT_FOUND)

            elif user_type == "SECONDARY":
                try:
                    member = Members.objects.get(phone_no_secondary_user=otp_obj.mobile_number)
                    user = otp_obj.mobile_number
                    data = {
                            'mobile': member.phone_no_secondary_user,
                            'user_type': 'SECONDARY',
                            'name': member.member_name,
                            'secondary_user_id': member.secondary_user_id,
                            'primary_name':member.primary_user_id.name,
                            'primary_user_id':member.primary_user_id.primary_user_id,
                            'primary_mobile_number':member.primary_user_id.phone_no_primary
                        }
                except Members.DoesNotExist:
                    return Response({'success': False, 'message': 'Secondary account does not exist'}, status=HTTP_404_NOT_FOUND)

            try:
                user = User.objects.get(username=user)
            except User.DoesNotExist:
                return Response({'success': False, 'message': ' User does not exist'}, status=HTTP_404_NOT_FOUND)

            token, created = Token.objects.get_or_create(user=user)
            data.update({"token": token.key})
            return Response({'success': True, 'message': 'OTP Verified Successfully', 'user_details': data}, status=HTTP_201_CREATED)


class OtpVerifyUserIdViewSet(CreateAPIView):
    queryset = OtpModels.objects.all()
    serializer_class = OTPVeifySerializerUserId

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data.get("otp", None)
        user_type = serializer.validated_data.get("user_type", None)
        user_id = serializer.validated_data.get("user_id", None)
        phone_number = serializer.validated_data.get("phone_number", None)

        try:
            otp_obj = OtpModels.objects.get(otp=otp)
            if (datetime.now(timezone.utc) - otp_obj.created_time).total_seconds() >= 1800:
                otp_obj.is_expired = True
                otp_obj.save()
                return Response({'success': False, 'message': 'Otp Expired'}, status=HTTP_400_BAD_REQUEST)
            if otp_obj.is_expired:
                return Response({'success': False, 'message': 'Otp Already Used'}, status=HTTP_400_BAD_REQUEST)
        except:
            return Response({'success': False, 'message': 'Invalid Otp'}, status=HTTP_400_BAD_REQUEST)
        else:
            if otp_obj:
                otp_obj.is_expired = True
                otp_obj.save()
            else:
                pass
            
            if user_type == "ADMIN":
                try:
                    admin = AdminProfile.objects.get(mobile_number=otp_obj.mobile_number)
                    user = admin.user
                    data = {
                        'mobile': admin.mobile_number,
                        'user_type': 'ADMIN',
                        'name': 'Admin',
                    }
                except AdminProfile.DoesNotExist:
                    return Response({'success': False, 'message': 'Admin account does not exist'}, status=HTTP_404_NOT_FOUND)
            
            elif user_type == "PRIMARY":
                try:
                    user_profile = FileUpload.objects.get(Q(phone_no_secondary=otp_obj.mobile_number) | Q(phone_no_primary=otp_obj.mobile_number))
                    user = otp_obj.mobile_number
                    mobile = user_profile.phone_no_primary if user_profile.phone_no_primary else user_profile.phone_no_secondary
                    data = {
                        'mobile': mobile,
                        'user_type': 'PRIMARY',
                        'name': user_profile.name.title(),
                        'primary_user_id': user_profile.primary_user_id
                    }
                except FileUpload.DoesNotExist:
                    return Response({'success': False, 'message': 'Primary account does not exist'}, status=HTTP_404_NOT_FOUND)

            elif user_type == "SECONDARY":
                try:
                    member = Members.objects.get(secondary_user_id=user_id)
                    if member.phone_no_secondary_user is None or member.phone_no_secondary_user == '':
                        member.phone_no_secondary_user = phone_number
                        member.save()
                        user = member.phone_no_secondary_user
                    else:
                        member.phone_no_secondary_user = otp_obj.mobile_number
                        user = otp_obj.mobile_number
                    data = {
                            'mobile': member.phone_no_secondary_user,
                            'user_type': 'SECONDARY',
                            'name': member.member_name.title(),
                            'secondary_user_id': member.secondary_user_id,
                            'primary_name':member.primary_user_id.name,
                            'primary_user_id':member.primary_user_id.primary_user_id,
                            'primary_mobile_number':member.primary_user_id.phone_no_primary
                        }
                except Members.DoesNotExist:
                    return Response({'success': False, 'message': 'Secondary account does not exist'}, status=HTTP_404_NOT_FOUND)

            try:
                user = User.objects.get(username=user)
            except User.DoesNotExist:
                return Response({'success': False, 'message': ' User does not exist'}, status=HTTP_404_NOT_FOUND)

            token, created = Token.objects.get_or_create(user=user)
            data.update({"token": token.key})
            return Response({'success': True, 'message': 'OTP Verified Successfully', 'user_details': data}, status=HTTP_201_CREATED)

class OtpVerifyUserCheckNumberViewSet(CreateAPIView):
    queryset = OtpModels.objects.all()
    serializer_class = OTPVeifySerializerUserId

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data.get("otp", None)
        user_type = serializer.validated_data.get("user_type", None)
        user_id = serializer.validated_data.get("user_id", None)
        phone_number = serializer.validated_data.get("phone_number", None)

        try:
            superusers = AdminProfile.objects.filter(user__is_superuser=True).first()
            admin_phonenumber = superusers.mobile_number
        except:
            admin_phonenumber = ''

        try:
            otp_obj = OtpModels.objects.get(otp=otp)
            if (datetime.now(timezone.utc) - otp_obj.created_time).total_seconds() >= 1800:
                otp_obj.is_expired = True
                otp_obj.save()
                return Response({'success': False, 'message': 'Otp Expired'}, status=HTTP_400_BAD_REQUEST)
            if otp_obj.is_expired:
                return Response({'success': False, 'message': 'Otp Already Used'}, status=HTTP_400_BAD_REQUEST)
        except:
            return Response({'success': False, 'message': 'Invalid Otp'}, status=HTTP_400_BAD_REQUEST)
        else:
            if otp_obj:
                otp_obj.is_expired = True
                otp_obj.save()
            else:
                pass
            
            if user_type == "ADMIN":
                try:
                    admin = AdminProfile.objects.get(mobile_number=otp_obj.mobile_number)
                    user = admin.user
                    data = {
                        'mobile': admin.mobile_number,
                        'user_type': 'ADMIN',
                        'name': 'Admin',
                    }
                except AdminProfile.DoesNotExist:
                    return Response({'success': False, 'message': 'Admin account does not exist'}, status=HTTP_404_NOT_FOUND)
            
            elif user_type == "PRIMARY":
                try:
                    if user_id:
                        user_profile = FileUpload.objects.get(Q(phone_no_secondary=otp_obj.mobile_number) | Q(phone_no_primary=otp_obj.mobile_number),primary_user_id=user_id)
                        user = otp_obj.mobile_number
                        mobile = user_profile.phone_no_primary if user_profile.phone_no_primary else user_profile.phone_no_secondary
                        data = {
                            'mobile': mobile,
                            'user_type': 'PRIMARY',
                            'name': user_profile.name.title(),
                            'primary_user_id': user_profile.primary_user_id
                        }
                    else:
                        user_profile = FileUpload.objects.get(Q(phone_no_secondary=otp_obj.mobile_number) | Q(phone_no_primary=otp_obj.mobile_number))
                        user = otp_obj.mobile_number
                        mobile = user_profile.phone_no_primary if user_profile.phone_no_primary else user_profile.phone_no_secondary
                        data = {
                            'mobile': mobile,
                            'user_type': 'PRIMARY',
                            'name': user_profile.name.title(),
                            'primary_user_id': user_profile.primary_user_id
                        }
                except FileUpload.DoesNotExist:
                    return Response({'success': False, 'message': 'Primary account does not exist'}, status=HTTP_404_NOT_FOUND)

            elif user_type == "SECONDARY":
                try:
                    member = Members.objects.get(secondary_user_id=user_id)
                    mems = Members.objects.filter(primary_user_id=member.primary_user_id).exclude(secondary_user_id=user_id)
                    if mems.count() >= 1:
                        for mem in mems:
                            if(mem.phone_no_secondary_user == phone_number) or mem.phone_no_secondary_user_secondary:
                                if(mem.phone_no_secondary_user == phone_number):
                                    mem.phone_no_secondary_user = None
                                    mem.save()
                                    mem.phone_no_secondary_user = mem.phone_no_secondary_user_secondary
                                    mem.phone_no_secondary_user_secondary = None
                                    mem.save()

                                    #if member.phone_no_secondary_user is None or member.phone_no_secondary_user == '':
                                    member.phone_no_secondary_user = phone_number
                                    member.save()
                                    user = member.phone_no_secondary_user
                                elif mem.phone_no_secondary_user_secondary == phone_number :
                                    mem.phone_no_secondary_user_secondary = None
                                    mem.save()
                                    #if member.phone_no_secondary_user is None or member.phone_no_secondary_user == '':
                                    member.phone_no_secondary_user = phone_number
                                    member.save()
                                    user = member.phone_no_secondary_user
                                else:
                                    pass
                            else:
                                pass

                    if member.primary_user_id.phone_no_primary == phone_number or member.primary_user_id.phone_no_secondary == phone_number:
                        if member.primary_user_id.phone_no_primary != None and member.primary_user_id.phone_no_secondary != None:
                            if member.primary_user_id.phone_no_secondary == phone_number:
                                # if member.phone_no_secondary_user is None or member.phone_no_secondary_user == '':
                                member.phone_no_secondary_user = phone_number
                                member.primary_user_id.phone_no_secondary = None
                                member.save()
                                member.primary_user_id.save()
                                user = member.phone_no_secondary_user
                                # else:
                                #     pass

                            elif member.primary_user_id.phone_no_primary  == phone_number:
                                # if member.phone_no_secondary_user is None or member.phone_no_secondary_user == '':
                                sec_number = member.primary_user_id.phone_no_secondary

                                member.primary_user_id.phone_no_secondary = None
                                member.primary_user_id.phone_no_primary = sec_number

                                member.phone_no_secondary_user = phone_number
                                member.save()
                                member.primary_user_id.save()
                                user = member.phone_no_secondary_user
                            else:
                                pass
                        elif(member.primary_user_id.phone_no_secondary == None):
                            # return Response({'success': False, 'message': 'Please contact admin'},status=HTTP_404_NOT_FOUND)
                            data = {
                                'admin_mobile_number' : admin_phonenumber,
                            }
                            return Response({'success': False, 'message': 'Please contact admin','user_details': data},
                            status=HTTP_404_NOT_FOUND)
                        else:
                            pass
                    elif member.phone_no_secondary_user is None or member.phone_no_secondary_user == '':
                        member.phone_no_secondary_user = phone_number
                        member.save()
                        user = member.phone_no_secondary_user
                    else:
                        member.phone_no_secondary_user = otp_obj.mobile_number
                        user = otp_obj.mobile_number
                    data = {
                            'mobile': member.phone_no_secondary_user,
                            'user_type': 'SECONDARY',
                            'name': member.member_name.title(),
                            'secondary_user_id': member.secondary_user_id,
                            'primary_name':member.primary_user_id.name,
                            'primary_user_id':member.primary_user_id.primary_user_id,
                            'primary_mobile_number':member.primary_user_id.phone_no_primary
                        }
                except Members.DoesNotExist:
                    return Response({'success': False, 'message': 'Secondary account does not exist'}, status=HTTP_404_NOT_FOUND)

            try:
                user = User.objects.get(username=user)
            except User.DoesNotExist:
                return Response({'success': False, 'message': ' User does not exist'}, status=HTTP_404_NOT_FOUND)

            token, created = Token.objects.get_or_create(user=user)
            data.update({"token": token.key})
            return Response({'success': True, 'message': 'OTP Verified Successfully', 'user_details': data}, status=HTTP_201_CREATED)


class UserCreateView(CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserCreateSerializer

    # def create(self, request):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     mobile_number = self.request.GET.get('mobile_number')
    #     user_type = self.request.GET.get('user_type')
    #
    #     user_name = serializer.validated_data.get("user_name", None)
    #     password = serializer.validated_data.get("password", None)
    #     confirm_password = serializer.validated_data.get("confirm_password", None)
    #
    #     if User.objects.filter(username=user_name).exists():
    #         return Response({'message': 'Username already exists','success':False},status=HTTP_400_BAD_REQUEST)
    #     if mobile_number and user_type:
    #         if user_type == 'PRIMARY':
    #             if(password ==  confirm_password):
    #                 user = User.objects.create(
    #                     username=user_name,
    #                 )
    #                 user.set_password(password)
    #                 user.save()
    #                 userprofile=UserProfile.objects.create(user=user,mobile_number = mobile_number,is_primary=True)
    #                 Notification.objects.create(user=userprofile,is_new_register=True,created_time=datetime.strptime('2018-02-16 11:00 AM', "%Y-%m-%d %I:%M %p"))
    #                 return Response({'success': True,'message':'User Profile Created Successfully'}, status=HTTP_201_CREATED)
    #             else:
    #                 return Response({'message': 'Password Missmatch','success':False},status=HTTP_400_BAD_REQUEST)
    #         elif user_type =='SECONDARY':
    #             if(password ==  confirm_password):
    #                 user = User.objects.create(
    #                     username=user_name,
    #                 )
    #                 user.set_password(password)
    #                 user.save()
    #                 userprofile=UserProfile.objects.create(user=user,mobile_number = mobile_number)
    #                 Notification.objects.create(user=userprofile,is_new_register=True,created_time=datetime.strptime('2018-02-16 11:00 AM', "%Y-%m-%d %I:%M %p"))
    #                 return Response({'success': True,'message':'User Profile Created Successfully'}, status=HTTP_201_CREATED)
    #             else:
    #                 return Response({'message': 'Password Missmatch','success':False},status=HTTP_400_BAD_REQUEST)
    #         elif user_type =='CHURCH':
    #             if(password ==  confirm_password):
    #                 user = User.objects.create(
    #                     username=user_name,
    #                 )
    #                 user.set_password(password)
    #                 user.save()
    #                 userprofile=UserProfile.objects.create(user=user,mobile_number = mobile_number,is_church_user=True)
    #                 Notification.objects.create(user=userprofile,is_new_register=True,created_time=datetime.strptime('2018-02-16 11:00 AM', "%Y-%m-%d %I:%M %p"))
    #                 return Response({'success': True,'message':'User Profile Created Successfully'}, status=HTTP_201_CREATED)
    #             else:
    #                 return Response({'message': 'Password Missmatch','success':False},status=HTTP_400_BAD_REQUEST)
    #         else:
    #             return Response({'message': 'Something Went Wrong','success':False},status=HTTP_400_BAD_REQUEST)
    #     else:
    #         return Response({'message': 'Something Went Wrong','success':False},status=HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    queryset = User.objects.all()
    serializer_class = LoginSerializer


#     def post(self, request, format=None):
#         serializer = LoginSerializer(data=request.data)
#         username =   request.data['username']
#         password =  request.data['password']
#         if not username:
#             return Response({'message': 'Username should not be blank','success':False},status=HTTP_400_BAD_REQUEST)
#         if not password:
#             return Response({'message': 'Password should not be blank','success':False},status=HTTP_400_BAD_REQUEST)
#         if username and password:
#             user = authenticate(username=username, password=password)
#             try:
#                 token, created = Token.objects.get_or_create(user=user)
#                 if user:
#                     if user.is_superuser==True:
#                         data = {
#                                 'username': user.username,
#                                 'token': token.key,
#                                 'user_type': "SUPERUSER"
#                                 }
#                         return Response({'success': True,'message':'Login Successfully','user-details':data}, status=HTTP_200_OK)
#                     else:
#                         userprofile = UserProfile.objects.filter(user=user)
#                         for userprofiles in userprofile:
#                             if userprofiles.is_primary ==True:
#                                 data = {
#                                 'username': user.username,
#                                 'token': token.key,
#                                 'user_type': "PRIMARY"
#                                 }
#                                 return Response({'success': True,'message':'Login Successfully','user-details':data}, status=HTTP_200_OK)
#                             elif userprofiles.is_church_user ==True:
#                                 data = {
#                                 'username': user.username,
#                                 'token': token.key,
#                                 'user_type': "CHURCH"
#                                 }
#                                 return Response({'success': True,'message':'Login Successfully','user-details':data}, status=HTTP_200_OK)
#                             elif userprofiles.is_church_user ==False and userprofiles.is_primary==False:
#                                 data = {
#                                 'username': user.username,
#                                 'token': token.key,
#                                 'user_type': "SECONDARY"
#                                 }
#                                 return Response({'success': True,'message':'Login Successfully','user-details':data}, status=HTTP_200_OK)
#                             else:
#                                 data = {
#                                 'username': user.username,
#                                 'token': token.key,
#                                 'user_type': "NO DATA"
#                                 }
#                                 return Response({'message': 'Something went wrong','success':False},status=HTTP_400_BAD_REQUEST)
#                 else:
#                     return Response({'message': 'Invalid credentials','success':False},status=HTTP_400_BAD_REQUEST)
#             except:
#                 return Response({'message': 'Invalid credentials','success':False},status=HTTP_400_BAD_REQUEST)
#         else:
#             return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 1000

class UserListCommonView(ListAPIView):
    queryset = FileUpload.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):

        context ={
            'request': request
        }
        term = None
        try:
            term = request.GET['term']
            if term:
                term = term.replace(" ", "")
                term.lower()
                queryset_primary = PrimaryUserSerializerPage(FileUpload.objects.filter(Q(name__nospaces__icontains =term)|Q(occupation__icontains=term)), many=True, context=context).data
                queryset_secondary = MembersSerializerPage(Members.objects.filter(Q(member_name__nospaces__icontains=term)|Q(occupation__icontains=term)), many=True, context=context).data
            else:
                queryset_primary = PrimaryUserSerializerPage(FileUpload.objects.all().order_by('name'), many=True, context=context).data
                queryset_secondary = MembersSerializerPage(Members.objects.all().order_by('member_name'), many=True, context=context).data
        except:
            queryset_primary = PrimaryUserSerializerPage(FileUpload.objects.all().order_by('name'), many=True, context=context).data
            queryset_secondary = MembersSerializerPage(Members.objects.all().order_by('member_name'), many=True, context=context).data
        # import pdb;pdb.set_trace()
        try:
            response = queryset_primary + queryset_secondary
        except:
            response =[]

        if term:
            res = sorted([x for x in response if (x['name'].replace(" ","").lower()).startswith(term.lower())], key = lambda i: i['name'])
            names = list(map(itemgetter('name'), res))
            response_query = res + sorted([x for x in response if x['name'] not in names], key = lambda i: i['name'])

        else:
            response_query = sorted(response, key = lambda i: i.get('name')) 
        responses = self.paginate_queryset(response_query)
        if responses is not None:
            serializer = CommonUserSerializer(responses,many=True)
            data = {
                'code': 200,
                'status': "OK",
            }
            page_nated_data = self.get_paginated_response(serializer.data).data
            data.update(page_nated_data)
            data['response'] = data.pop('results')
            return Response(data)

        serializer = CommonUserSerializer(response,many=True)
        output = serializer.data
        data={
            'response': output

            }
        data['response'] = data.pop('results')
        return Response(data)


class FamilyListView(ListAPIView):
    queryset = Family.objects.all().order_by('name')
    serializer_class = FamilyListSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            data = {
                'code': 200,
                'status': "OK",
            }

            page_nated_data = self.get_paginated_response(serializer.data).data
            data.update(page_nated_data)
            data['response'] = data.pop('results')

            return Response(data)


        serializer = self.get_serializer(queryset, many=True)

        data = {
            'code': 200,
            'status': "OK",
            'response': serializer.data
        }

        return Response(data)

class UserUpdateView(RetrieveUpdateAPIView):
    queryset = FileUpload.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]

    # def


class UserDeleteView(DestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]


class UserDetailView(APIView):
    queryset = FileUpload.objects.all()
    serializer_class = UserRetrieveSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request,*args,**kwargs):
        usertype_to = None
        usertype_from = None
        request_from = None
        request_to = None
        is_accepted = False
        member = None
        date_om = None
        
        user_type=request.GET['user_type']
        if not user_type:
            return Response({'success': False,'message':'Please provide user type'}, status=HTTP_400_BAD_REQUEST)

        try:
            member=FileUpload.objects.get(phone_no_primary=self.request.user.username)

            if member:
                request_from = member
                usertype_from = 'PRIMARY'
        except:
            member=Members.objects.filter(phone_no_secondary_user=self.request.user.username)

            if member:
                request_from = member
                usertype_from = 'SECONDARY'

        try:
            if user_type=='SECONDARY':
                user_details=Members.objects.get(secondary_user_id=self.kwargs['pk'])
                request_to = user_details
                usertype_to = 'SECONDARY'
                try:
                    phoneobj=ViewRequestNumber.objects.filter(request_from=member.pk,usertype_from=usertype_from,request_to=request_to.pk,usertype_to=usertype_to)
                    is_accepted = phoneobj.first().is_accepted
                except:
                    is_accepted = False
                try:
                    image=request.build_absolute_uri(user_details.image.url)
                except:
                    image='null'
                try :
                    if user_details.marrige_date :
                        date_om = user_details.marrige_date
                    elif user_details.dom:
                        date_om = user_details.dom
                    else:
                        pass
                except:
                    date_om = None

                try:
                    family_id = user_details.primary_user_id.get_file_upload.first().id
                except:
                    family_id = None
                try:
                    family_name = user_details.primary_user_id.get_file_upload.first().name
                except:
                    family_name = None
                data={
                    'name':user_details.member_name,
                    'relation':user_details.relation,
                    'dob':user_details.dob,
                    'dom':date_om,
                    # 'image':user_details.image,
                    'is_accepted':is_accepted,
                    'phone_no_secondary_user':user_details.phone_no_secondary_user,
                    'phone_no_secondary_user_secondary':user_details.phone_no_secondary_user_secondary,
                    'primary_user':user_details.primary_user_id.name,
                    'primary_user_id':user_details.primary_user_id.primary_user_id,
                    'blood_group':user_details.blood_group,
                    'email':user_details.email,
                    'occupation':user_details.occupation,
                    'about':user_details.about,
                    'marital_status':user_details.marital_status,
                    'marrige_date':date_om,
                    'in_memory':user_details.in_memory,
                    'in_memory_date':user_details.in_memory_date,
                    'image':image,
                    'primary_in_memory':user_details.primary_user_id.in_memory,
                    'family_id':family_id,
                    'family_name':family_name,
                    'primary_user_name':user_details.primary_user_id.name,
                    'user_type':'SECONDARY',
                    'landline':user_details.landline

                }
                return Response({'success': True,'message':'Profile found successfully','user_details':data}, status=HTTP_200_OK)
            else:
                try:
                    user_details=FileUpload.objects.get(primary_user_id=self.kwargs['pk'])

                    request_to = user_details
                    usertype_to = 'PRIMARY'
                    try:
                        phoneobj=ViewRequestNumber.objects.filter(request_from=member.pk, usertype_from=usertype_from,\
                            request_to=request_to.pk, usertype_to=usertype_to)
                        is_accepted = phoneobj.first().is_accepted
                    except:
                        is_accepted = False
                    try:
                        image=request.build_absolute_uri(user_details.image.url)
                    except:
                        image='null'
                    try :
                        if user_details.marrige_date :
                            date_om = user_details.marrige_date
                        elif user_details.dom:
                            date_om = user_details.dom
                        else:
                            pass
                    except:
                        date_om = None

                    try:
                        family_id = user_details.get_file_upload.first().id
                    except:
                        family_id = None

                    try:
                        family_name = user_details.get_file_upload.first().name
                    except:
                        family_name = None

                    data={
                       # 'member_name':user_details.primary_user_id,
                       'name':user_details.name,
                       'address':user_details.address,
                       'is_accepted':is_accepted,
                       'phone_no_primary':user_details.phone_no_primary,
                       'phone_no_secondary':user_details.phone_no_secondary,
                       'dob':user_details.dob,
                       'dom':date_om,
                       'blood_group':user_details.blood_group,
                       'email':user_details.email,
                       'occupation':user_details.occupation,
                       'about':user_details.about,
                       'marital_status':user_details.marital_status,
                       'marrige_date':date_om,
                       'in_memory':user_details.in_memory,
                       'in_memory_date':user_details.in_memory_date,
                       'image':image,
                       'relation':user_details.relation,
                       'family_id':family_id,
                       'family_name':family_name,
                       'primary_user_name':user_details.name,
                       'user_type':'PRIMARY',
                       'landline':user_details.landline
                    }
                    return Response({'success': True,'message':'Profile found successfully','user_details':data}, status=HTTP_200_OK)
                except:
                    user_details=AdminProfile.objects.get(id=self.kwargs['pk'])
                    data={
                        'id':user_details.user,
                        'mobile_number':user_details.mobile_number
                    }
                    return Response({'success': True,'message':'Profile found successfully','user_details':data}, status=HTTP_200_OK)
        except:
            return Response({'success': False,'message':'Something Went Wrong'}, status=HTTP_400_BAD_REQUEST)


class ChurchVicarView(RetrieveAPIView):
    queryset = ChurchDetails.objects.all()
    serializer_class = ChurchVicarSerializer
    permission_classes = [AllowAny]

class ChurchVicarEditView(viewsets.ModelViewSet):
    queryset = ChurchDetails.objects.all()
    serializer_class = ChurchVicarSerializer
    permission_classes = [AllowAny]

class ChurchHistoryView(RetrieveAPIView):
    queryset = ChurchDetails.objects.all()
    serializer_class = ChurchHistorySerializer
    permission_classes = [AllowAny]

class ChurchHistoryEditView(viewsets.ModelViewSet):
    queryset = ChurchDetails.objects.all()
    serializer_class = ChurchHistorySerializer
    permission_classes = [AllowAny]

class ChurchImagesView(RetrieveAPIView):
    queryset = ChurchDetails.objects.all()
    serializer_class = ChurchImagesSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class PostsViewset(viewsets.ModelViewSet):
    serializer_class = ChurchImagesSerializer
    parser_classes = (MultipartJsonParser, parsers.JSONParser)
    queryset = FileUpload.objects.all()
    # lookup_field = 'id'


class SecondaryaddView(CreateAPIView):
    queryset = FileUpload.objects.all()
    serializer_class = SecondaryaddSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user_id = self.kwargs['pk']
        secondary_users = request.data['secondary_user_id']
        try:
            if secondary_users:
                user_instance = FileUpload.objects.get(primary_user_id=user_id)
                if user_instance:
                    for secondary_user in secondary_users:
                        sec_user = Members.objects.get(secondary_user_id=secondary_user)
                        user_instance.get_primary_user.add(sec_user)
                    total_count = user_instance.get_primary_user.count()
                    total_count=total_count+1
                    Notification.objects.create(user=user_instance,is_user_add_new_member=True,created_time=datetime.strptime('2018-02-16 11:00 AM', "%Y-%m-%d %I:%M %p"))
                    return Response({'success': True,'message':'Secondary User Added Successfully'}, status=HTTP_201_CREATED)
                else:
                   # raise serializers.ValidationError("You don't have permission to add family members")
                   return Response({'success': False,'message': 'You dont have permission to add family members'}, status=HTTP_400_BAD_REQUEST)
            else:
                return Response({'success': False,'message': 'Something Went Wrong'}, status=HTTP_400_BAD_REQUEST)
        except:
            return Response({'success': False,'message': 'Something Went Wrong'}, status=HTTP_400_BAD_REQUEST)


class PrayerGroupaddView(CreateAPIView):
    queryset = PrayerGroup.objects.all()
    serializer_class = PrayerGroupAddSerializer
    permission_classes = [IsAdminUser]


class PrayerGroupMemberaddView(RetrieveUpdateAPIView):
    queryset = PrayerGroup.objects.all()
    serializer_class = PrayerGroupAddMembersSerializer
    permission_classes = [IsAdminUser]



    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     prayer_id = self.kwargs['pk']
    #     prayer_profiles = serializer.validated_data.get('user_profile',None)
    #     try:
    #         if prayer_profiles:
    #             prayer_instance = PrayerGroup.objects.get(id=prayer_id)
    #             for prayer_profile in prayer_profiles:
    #                 member_user = FileUpload.objects.get(id=prayer_profile.primary_user_id)
    #                 prayer_instance.user_profile.add(member_user)
    #             return Response({'success': True,'message':'Group member Added Successfully'}, status=HTTP_201_CREATED)
    #         else:
    #             return Response({'success': False,'message': 'Something Went Wrong'}, status=HTTP_400_BAD_REQUEST)
    #     except:
    #         return Response({'success': False,'message': 'Something Went Wrong'}, status=HTTP_400_BAD_REQUEST)


class PrayerGrouplistView(ListAPIView):
    queryset = PrayerGroup.objects.all().order_by('name')
    serializer_class = PrayerGroupAddSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            data = {
                'code': 200,
                'status': "OK",
            }

            page_nated_data = self.get_paginated_response(serializer.data).data
            data.update(page_nated_data)
            data['response'] = data.pop('results')

            return Response(data)


        serializer = self.get_serializer(queryset, many=True)

        data = {
            'code': 200,
            'status': "OK",
            'response': serializer.data
        }

        return Response(data)



class PrayerGroupBasedFamilyView(ListAPIView):
    queryset = Family.objects.all()
    serializer_class = FamilyListSerializer
    permission_classes = [AllowAny]
    # pagination_class = StandardResultsSetPagination

    def get_queryset(self, *args, **kwargs):
        prayer_id = self.kwargs['pk']
        
        try:
            prayer_group = PrayerGroup.objects.get(id=prayer_id)
        except PrayerGroup.DoesNotExist:
            raise exceptions.NotFound(detail="Prayer group does not exist")
        family_list1 = prayer_group.family.all()
        family_list1 = family_list1.filter(primary_user_id=None)
        family_list2 = Family.objects.filter(primary_user_id__in=prayer_group.primary_user_id.all())
        family_list = family_list1 | family_list2
        return family_list

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            data = {
                'code': 200,
                'status': "OK",
            }

            page_nated_data = self.get_paginated_response(serializer.data).data
            data.update(page_nated_data)
            data['response'] = data.pop('results')

            return Response(data)


        serializer = self.get_serializer(queryset, many=True)

        data = {
            'code': 200,
            'status': "OK",
            'response': serializer.data
        }

        return Response(data)


class PrayerGroupBasedMembersView(ListAPIView):
    queryset = PrayerGroup.objects.all()
    serializer_class = MembersSerializer
    permission_classes = [AllowAny]
    # pagination_class = StandardResultsSetPagination

    def get_queryset(self, *args, **kwargs):
        prayer_id = self.kwargs['pk']

        try:
            prayer_group = PrayerGroup.objects.get(id=prayer_id)
        except PrayerGroup.DoesNotExist:
            raise exceptions.NotFound(detail="Prayer group does not exist")
        self.primary_user = prayer_group.primary_user_id
        member_list = Members.objects.filter(primary_user_id__in=prayer_group.primary_user_id.all())
        return member_list

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            data = {
                'code': 200,
                'status': "OK",
            }

            page_nated_data = self.get_paginated_response(serializer.data).data
            data.update(page_nated_data)
            data['response'] = data.pop('results')
            return Response(data)
        serializer = self.get_serializer(queryset, many=True)

        data = {
            'code': 200,
            'status': "OK",
            'response': serializer.data
        }



        for primary_user in self.primary_user.all():
            primary_user_id = UserRetrieveSerializer(primary_user,context={'request':request}).data

            data['response'].insert(0, primary_user_id)

        return Response(data)


#
# class FamilyMemberList(ListAPIView):
#     lookup_field = 'pk'
#     queryset = Family.objects.all()
#     serializer_class = MembersSerializer
#     permission_classes = [AllowAny]
#
#     def get_queryset(self, *args, **kwargs):
#         family_id = self.kwargs['pk']
#         try:
#             family = Family.objects.get(id=family_id)
#         except Family.DoesNotExist:
#             raise exceptions.NotFound(detail="Family does not exist")
#
#         self.primary_user = family.primary_user_id
#
#         members = Members.objects.filter(primary_user_id=family.primary_user_id)
#         return members
#
#     def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
#
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#
#             data = {
#                 'code': 200,
#                 'status': "OK",
#             }
#
#             page_nated_data = self.get_paginated_response(serializer.data).data
#             data.update(page_nated_data)
#             data['response'] = data.pop('results')
#
#             primary_user_id =UserRetrieveSerializer(self.primary_user).data
#
#             data['response'].insert(0, primary_user_id)
#
#             return Response(data)
#
#
#         serializer = self.get_serializer(queryset, many=True)
#
#         data = {
#             'code': 200,
#             'status': "OK",
#             'response': serializer.data
#         }
#
#         primary_user_id = UserRetrieveSerializer(self.primary_user).data
#
#         data['response'].insert(0, primary_user_id)
#
#         return Response(data)



class FamilyMemberList(ListAPIView):
    lookup_field = 'pk'
    queryset = Family.objects.all()
    serializer_class = MembersSerializer
    permission_classes = [AllowAny]

    def get_queryset(self, *args, **kwargs):
        family_id = self.kwargs['pk']
        try:
            family = Family.objects.get(id=family_id)
        except Family.DoesNotExist:
            raise exceptions.NotFound(detail="Family does not exist")

        self.primary_user = family.primary_user_id

        members = Members.objects.filter(primary_user_id=family.primary_user_id)
        return members

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            data = {
                'code': 200,
                'status': "OK",
            }

            page_nated_data = self.get_paginated_response(serializer.data).data
            data.update(page_nated_data)
            data['response'] = data.pop('results')
            primary_user_id =UserRetrieveSerializer(self.primary_user, context={'request':request}).data

            data['response'].insert(0, primary_user_id)

            return Response(data)


        serializer = self.get_serializer(queryset, many=True)

        data = {
            'code': 200,
            'status': "OK",
            'response': serializer.data
        }

        primary_user_id = UserRetrieveSerializer(self.primary_user, context={'request':request}).data

        data['response'].insert(0, primary_user_id)
        
        return Response(data)

class NoticeModelViewSet(ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        data = {
                'code': 200,
                'status': "OK",
        }
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        data['response'] = serializer.data
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = {
            'code': 200,
            'status': "OK",
        }
        data['response'] = serializer.data
        return Response(data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = {
            'code': 200,
            'status': "OK",
        }
        data['response'] = serializer.data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        data = {
            'code': 200,
            'status': "OK",
        }
        data['response'] = "Successfully deleted"
        return Response(data)

    def update(self, request, *args, **kwargs):

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = {
            'code': 200,
            'status': "Successfully updated",
        }
        data['response'] = serializer.data
        return Response(data)


class SendOtp(APIView):
    queryset = FileUpload.objects.all()
    serializer_class = UserRegistrationMobileSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        mobile_number = self.request.query_params.get('mobile_number')
        user_id = self.request.query_params.get('user_id')
        try:
            sec_user = Members.objects.get(secondary_user_id=user_id)
            sec_user.phone_no_secondary_user=mobile_number
            sec_user.save()
            user,created=User.objects.get_or_create(username=mobile_number)
            token, created = Token.objects.get_or_create(user=user)
            otp_number = get_random_string(length=6, allowed_chars='1234567890')
            primary_mobile_number = sec_user.primary_user_id.phone_no_primary
            try:
                OtpModels.objects.filter(mobile_number=sec_user.primary_user_id.phone_no_primary).delete()
            except:
                pass

            OtpModels.objects.create(mobile_number=primary_mobile_number, otp=otp_number)


            message_body = sec_user.member_name.title() + ' requested OTP for login: ' + otp_number
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(to='+91' + mobile_number, from_='+15036837180',body=message_body)

            requests.get(
                "http://unifiedbuzz.com/api/insms/format/json/?mobile=" + primary_mobile_number + "&text=" + message_body +
                "&flash=0&type=1&sender=MARCHR",
                headers={"X-API-Key": "918e0674e62e01ec16ddba9a0cea447b"})
            try:
                superusers = AdminProfile.objects.filter(user__is_superuser=True).first()
                admin_phonenumber = superusers.mobile_number
            except:
                admin_phonenumber = ''
            data = {
                'mobile': mobile_number,
                'admin_mobile_number' : admin_phonenumber,
                'user_type': 'SECONDARY',
                'name': sec_user.member_name,
                'token':token.key,
                'primary_user_name':sec_user.primary_user_id.name,
                'primary_mobile_number':sec_user.primary_user_id.phone_no_primary
            }
            return Response({'success': True, 'message': 'OTP Sent Successfully','user_details': data},
                            status=HTTP_200_OK)

        except Members.DoesNotExist:
            raise exceptions.NotFound(detail="User does not exist")
        
        superusers = User.objects.filter(is_superuser=True).first()
        
        # if user.primary_user_id:
        #     return Response({'success': False,'message': superusers.}, status=HTTP_400_BAD_REQUEST)


class SendOtpSecSave(APIView):
    queryset = FileUpload.objects.all()
    serializer_class = UserRegistrationMobileSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        mobile_number = self.request.query_params.get('mobile_number')
        user_id = self.request.query_params.get('user_id')
        try:
            superusers = AdminProfile.objects.filter(user__is_superuser=True).first()
            admin_phonenumber = superusers.mobile_number
        except:
            admin_phonenumber = ''
        try:
            sec_user = Members.objects.get(secondary_user_id=user_id)
            user,created=User.objects.get_or_create(username=mobile_number)
            token, created = Token.objects.get_or_create(user=user)
            otp_number = get_random_string(length=6, allowed_chars='1234567890')
            primary_mobile_number = sec_user.primary_user_id.phone_no_primary
            try:
                OtpModels.objects.filter(mobile_number=sec_user.primary_user_id.phone_no_primary).delete()
            except:
                pass

            OtpModels.objects.create(mobile_number=primary_mobile_number, otp=otp_number)


            message_body = sec_user.member_name + ' requested OTP for login: ' + otp_number
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(to='+91' + mobile_number, from_='+15036837180',body=message_body)

            requests.get(
                "http://unifiedbuzz.com/api/insms/format/json/?mobile=" + primary_mobile_number + "&text=" + message_body +
                "&flash=0&type=1&sender=MARCHR",
                headers={"X-API-Key": "918e0674e62e01ec16ddba9a0cea447b"})

            data = {
                'mobile': mobile_number,
                'admin_mobile_number' : admin_phonenumber,
                'user_type': 'SECONDARY',
                'name': sec_user.member_name,
                'token':token.key,
                'primary_user_name':sec_user.primary_user_id.name,
                'primary_mobile_number':sec_user.primary_user_id.phone_no_primary,
                'user_id':user_id,
            }
            return Response({'success': True, 'message': 'OTP Sent Successfully','user_details': data},
                            status=HTTP_200_OK)

        except Members.DoesNotExist:
            data = {
                'admin_mobile_number' : admin_phonenumber,
            }
            return Response({'success': False, 'message': 'User does not exist','user_details': data},
                            status=HTTP_404_NOT_FOUND)

        # superusers = User.objects.filter(is_superuser=True).first()

        # if user.primary_user_id:
        #     return Response({'success': False,'message': superusers.}, status=HTTP_400_BAD_REQUEST)

class SendWithoutOtpSecSave(APIView):
    queryset = FileUpload.objects.all()
    serializer_class = UserRegistrationMobileSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        mobile_number = self.request.query_params.get('mobile_number')
        user_id = self.request.query_params.get('user_id')
        try:
            superusers = AdminProfile.objects.filter(user__is_superuser=True).first()
            admin_phonenumber = superusers.mobile_number
        except:
            admin_phonenumber = ''
        try:
            sec_user = Members.objects.get(secondary_user_id=user_id)
            user,created=User.objects.get_or_create(username=mobile_number)
            token, created = Token.objects.get_or_create(user=user)
            otp_number = get_random_string(length=6, allowed_chars='1234567890')
            primary_mobile_number = sec_user.primary_user_id.phone_no_primary
            try:
                OtpModels.objects.filter(mobile_number=sec_user.primary_user_id.phone_no_primary).delete()
            except:
                pass

            # OtpModels.objects.create(mobile_number=primary_mobile_number, otp=otp_number)


            # message_body = sec_user.member_name + ' requested OTP for login: ' + otp_number
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(to='+91' + mobile_number, from_='+15036837180',body=message_body)

            # requests.get(
            #     "http://unifiedbuzz.com/api/insms/format/json/?mobile=" + primary_mobile_number + "&text=" + message_body +
            #     "&flash=0&type=1&sender=MARCHR",
            #     headers={"X-API-Key": "918e0674e62e01ec16ddba9a0cea447b"})

            data = {
                'mobile': mobile_number,
                'admin_mobile_number' : admin_phonenumber,
                'user_type': 'SECONDARY',
                'name': sec_user.member_name,
                'token':token.key,
                'primary_user_name':sec_user.primary_user_id.name,
                'primary_mobile_number':sec_user.primary_user_id.phone_no_primary,
                'user_id':user_id,
            }
            return Response({'success': True, 'message': 'OTP Sent Successfully','user_details': data},
                            status=HTTP_200_OK)

        except Members.DoesNotExist:
            data = {
                'admin_mobile_number' : admin_phonenumber,
            }
            return Response({'success': False, 'message': 'User does not exist','user_details': data},
                            status=HTTP_404_NOT_FOUND)

class Profile(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        if hasattr(request.user, 'adminprofile'):
            serializer = AdminProfileSerializer(request.user.adminprofile)

            return Response({'success': True,'message':'Profile found successfully','user_details':serializer.data}, status=HTTP_200_OK)
        
        primary_user = FileUpload.objects.filter(phone_no_primary=request.user.username)

        if primary_user.exists():
            serializer = PrimaryUserProfileSerializer(primary_user.first(), context = {'request':request})

            return Response({'success': True,'message':'Profile found successfully','user_details':serializer.data}, status=HTTP_200_OK)

        member = Members.objects.filter(phone_no_secondary_user=request.user.username)

        if member.exists():
            serializer = MemberProfileSerializer(member.first(), context = {'request':request})

            return Response({'success': True,'message':'Profile found successfully','user_details':serializer.data}, status=HTTP_200_OK)

        data = {
            'status': 'Not Found'
        }
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, format=None):
        serializer = None

        if hasattr(request.user, 'adminprofile'):
            serializer = AdminProfileSerializer(request.user.adminprofile, data=request.data)

        member = Members.objects.filter(phone_no_secondary_user=request.user.username)

        if member.exists():
            serializer = MemberProfileSerializer(member.first(), data=request.data, context = {'request':request})

        primary_user = FileUpload.objects.filter(phone_no_primary=request.user.username)

        if primary_user.exists():
            serializer = PrimaryUserProfileSerializer(primary_user.first(), data=request.data, context = {'request':request})

        if serializer:
            if serializer.is_valid():
                serializer.save()

                data = {
                    'success': True,
                    'message':'Profile found successfully',
                    'user_details':serializer.data
                }

                return Response(data, status=status.HTTP_200_OK)

            data = {
                    'success': False,
                    'message':'invalid input data',
                    'user_details':serializer.data
            }
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'status': 'Not Found'
        }
        return Response(data, status=status.HTTP_404_NOT_FOUND)

       
# class NoticeBereavementView(ModelViewSet):
#     queryset=NoticeBereavement.objects.all()
#     serializer_class = NoticeBereavementSerializer
#     permission_classes = [IsAdminUser]
#
#     def create(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         title = serializer.validated_data.get("title", None)
#         description = serializer.validated_data.get("description", None)
#         prayer_group = serializer.validated_data.get("prayer_group", None)
#         family = serializer.validated_data.get("family", None)
#         primary_member = serializer.validated_data.get("primary_member", None)
#         secondary_member = serializer.validated_data.get("secondary_member", None)
#         user_type=serializer.validated_data.get("user_type", None)
#         if user_type=='SECONDARY':
#             secondary_id=Members.objects.filter(secondary_user_id=secondary_member)





class FamilyMemberDetails(ListAPIView):
    lookup_field = 'pk'
    queryset = Family.objects.all()
    serializer_class = MembersDetailsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):

        try:
            primary_user = FileUpload.objects.get(phone_no_primary=self.request.user.username)
            members = Members.objects.filter(primary_user_id=primary_user)
            self.primary_user = primary_user
        except:
            secondary_user = Members.objects.get(phone_no_secondary_user=self.request.user.username)
            members = Members.objects.filter(primary_user_id=secondary_user.primary_user_id)
            self.primary_user = secondary_user.primary_user_id

        return members

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            data = {
                'code': 200,
                'status': "OK",
            }

            page_nated_data = self.get_paginated_response(serializer.data).data
            
            data.update(page_nated_data)
            # data['response'] = data.pop('results')

            primary_user_id =UserDetailsRetrieveSerializer(self.primary_user,context={'request':request}).data

            
            data['response'] = {'family_members':data}
            data['response']['family_members'].insert(0, primary_user_id)
            return Response(data)


        serializer = self.get_serializer(queryset, many=True)

        data = {
            'code': 200,
            'status': "OK",
            
        }

        primary_user_id = UserDetailsRetrieveSerializer(self.primary_user,context={'request':request}).data

        try:
            family_images = self.primary_user.get_file_upload.first().image.url
            family_image=request.build_absolute_uri(family_images)
        except:
            family_image = None
        try:
            prayer_group_name = self.primary_user.get_file_upload_prayergroup.first().name
            prayer_group_id = self.primary_user.get_file_upload_prayergroup.first().id
        except:
            prayer_group_name = None
            prayer_group_id = None
        
        if self.primary_user.get_file_upload.first():
            data['response'] = {
                'family_members':serializer.data,
                'family_name':self.primary_user.get_file_upload.first().name.title(),
                'family_about':self.primary_user.get_file_upload.first().about,
                'family_image':family_image,
                'family_id': self.primary_user.get_file_upload.first().id,
                'prayer_group_name' : prayer_group_name,
                'prayer_group_id' : prayer_group_id
            }
        else:
            data['response'] = {
                'family_members':serializer.data,
                'family_name':None,
                'family_about':None,
                'family_image':family_image,
                'family_id' : None,
                'prayer_group_name' : prayer_group_name,
                'prayer_group_id' : prayer_group_id
            }

        data['response']['family_members'].insert(0, primary_user_id)
        


        return Response(data)


class UnapprovedMemberView(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    lookup_field = 'pk'
    queryset = UnapprovedMember.objects.all()
    serializer_class = UnapprovedMemberSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsPrimaryUserOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        data ={
            "success": True,
            'message': "Secondary user submitted successfully, wait for admin approval to reflect changes"
        }
        data['response'] = serializer.data

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        data ={
            "success": True,
            "code": 200,
        }

        data['response'] = serializer.data

        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        data ={
            "success": True,
            "code": 200,
        }

        data['response'] = serializer.data

        return Response(data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        data ={
            "success": True,
            "code": 200,
        }

        data['response'] = serializer.data

        return Response(data)

    @action(methods=['get'], detail=True, url_path='approve-member',
        permission_classes=[IsAuthenticated, AdminPermission])
    def approve_member(self, request, pk=None):
        # import pdb;pdb.set_trace()
        member = self.get_object()

        data = UnapprovedMemberSerializer(member).data
        data.pop('secondary_user_id')
        data.pop('rejected')
        data.pop('status')
        data.pop('date')
        data.pop('type')
        data.pop('primary_user_number')
        data.pop('primary_user_name')
        data.pop('family_name')
        data.pop('prayer_group_name')
        data.pop('date_format')
        
        try:
            img_name = data.get('image').split('/')[-1]
            img_path = 'members/'+img_name
            data['image'] = img_path
        except:
            pass
        edit_user = data.pop('edit_user')
        if edit_user:
            Members.objects.filter(secondary_user_id=edit_user).update(**data)
        else:
            primary_user = FileUpload.objects.get(pk=data.pop('primary_user_id'))

            Members.objects.create(primary_user_id=primary_user, **data)
            try:
                user_details_str = "Your request to add %s has been accepted. The profile is listed in your family."%(member.member_name)
                not_obj = Notification.objects.create(created_by_primary=primary_user,
                          message=user_details_str)
                NoticeReadPrimary.objects.create(notification=not_obj, user_to=primary_user)
                member.status = 'Accepted'
                member.save() 
            except:
                pass
            try:
                image = ""
                user=User.objects.get(username=primary_user.phone_no_primary)
                content = {'title':'New Member Request','message':{"data":{"title":"New Member","body":"Your request to add %s has been accepted. The profile is listed in your family"%(member.member_name),"notificationType":"default","backgroundImage":image,"text_type":"long"},\
                "notification":{"alert":"This is a FCM notification","title":"New Member","body":"Your request to add %s has been accepted. The profile is listed in your family."%(member.member_name),"sound":"default","backgroundImage":image,"backgroundImageTextColour":"#FFFFFF","image":image,"click_action":"default"}} } 
                
                content_ios = {'message':{"aps":{"alert":{"title":"New Member","subtitle":"","body":"Your request to add %s has been accepted. The profile is listed in your family"%(member.member_name)},"sound":"default","category":"default","badge":1,"mutable-content":1},"media-url":image}}
                resp = fcm_messaging_to_user(user,content)
                resp1 = apns_messaging_to_user(user,content_ios) 
            except:
                pass
        # member.delete()

        return Response({'success': True})

    @action(methods=['get'], detail=True, url_path='reject-member',
        permission_classes=[IsAuthenticated, AdminPermission])
    def reject_member(self, request, pk=None):
        member = self.get_object()
        try:
            user_details_str = user_details_str = 'Admin has rejected your request to add %s to your family list.Please contact admin for further information.'%(member.member_name)
            not_obj = Notification.objects.create(created_by_primary=member.primary_user_id,
                      message=user_details_str)
            NoticeReadPrimary.objects.create(notification=not_obj, user_to=member.primary_user_id)
        except:
            pass
        try:
            image = ""
            user=User.objects.get(username=member.primary_user_id.phone_no_primary)
            content = {'title':'New Member Request','message':{"data":{"title":"Request Rejected","body":"Admin has rejected your request to add %s to your family list.Please contact admin for further information"%(member.member_name),"notificationType":"default","backgroundImage":image,"text_type":"long"},\
            "notification":{"alert":"This is a FCM notification","title":"Request Rejected","body":"Admin has rejected your request to add %s to your family list.Please contact admin for further information."%(member.member_name),"sound":"default","backgroundImage":image,"backgroundImageTextColour":"#FFFFFF","image":image,"click_action":"default"}} } 
            
            content_ios = {'message':{"aps":{"alert":{"title":"Request Rejected","subtitle":"","body":"Admin has rejected your request to add %s to your family list.Please contact admin for further information"%(member.member_name)},"sound":"default","category":"default","badge":1,"mutable-content":1},"media-url":image}}
            resp = fcm_messaging_to_user(user,content)
            resp1 = apns_messaging_to_user(user,content_ios) 
        except:
            pass      
        member.rejected = True
        member.status  = 'Rejected'
        member.save()
        return Response({'success': True})

class FamilyDetailView(ListAPIView):
    queryset = Family.objects.all()
    serializer_class = MembersSerializer
    permission_classes = [AllowAny]

    def get_queryset(self, *args, **kwargs):
        family_id = self.kwargs['pk']
        try:
            family = Family.objects.get(id=family_id)
        except Family.DoesNotExist:
            raise exceptions.NotFound(detail="Family does not exist")

        self.primary_user = family.primary_user_id
        self.family_obj = family
        members = Members.objects.filter(primary_user_id=family.primary_user_id)
        return members

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            data = {
                'code': 200,
                'status': "OK",
            }

            page_nated_data = self.get_paginated_response(serializer.data).data
            data.update(page_nated_data)
            # data['response'] = data.pop('results')

            primary_user_id =UserDetailsRetrieveSerializer(self.primary_user,context={'request':request}).data


            data['response'] = {'family_members':data}
            data['response']['family_members'].insert(0, primary_user_id)
            return Response(data)


        serializer = self.get_serializer(queryset, many=True)

        data = {
            'code': 200,
            'status': "OK",

        }

        primary_user_id = UserDetailsRetrieveSerializer(self.primary_user,context={'request':request}).data
        # family = Family.objects.get(primary_user_id=primary_user_id)
        # import pdb;pdb.set_trace()
        try:
            family_image = request.build_absolute_uri(self.primary_user.get_file_upload.first().image.url)
        except:
            family_image = None

        try:
            family_images = request.build_absolute_uri(self.family_obj.image.url)
        except:
            family_images = None
        # import pdb;pdb.set_trace()
        try:
            if self.primary_user.get_file_upload.first() :
                data['response'] = {
                    'family_members':serializer.data,
                    'family_name':self.primary_user.get_file_upload.first().name,
                    'family_about':self.primary_user.get_file_upload.first().about,
                    'family_image':family_image
                    }
                data['response']['family_members'].insert(0, primary_user_id)

        except:
            data['response'] = {
                'family_members':[],
                'family_name':self.family_obj.name,
                'family_about':self.family_obj.about,
                'family_image':family_images
            }

        return Response(data)

#
# class ViewRequestNumberView(APIView):
#     queryset=

class NoticeBereavementCreate(CreateAPIView):
    queryset = NoticeBereavement.objects.all()
    serializer_class = NoticeBereavementSerializer
    permission_classes = [IsAdminUser]

    def post(self, request):
        prayer_group_id = request.POST.get('prayer_group_id', False)
        family_id = request.POST.get('family_id', False)
        member_id=request.POST.get('member_id', False)
        user_type=request.POST.get('user_type', False)
        description=request.POST.get('description', False)
        # title=request.POST.get('title', False)
        if not prayer_group_id and not family_id and not member_id and not description:
            return Response({'success': False,'message': 'You should fill all the fields'}, status=HTTP_400_BAD_REQUEST)
        else:
            if not prayer_group_id:
                return Response({'success': False,'message': 'Prayer group field shouldnot be blank'}, status=HTTP_400_BAD_REQUEST)
            if not family_id:
                return Response({'success': False,'message': 'Family field shouldnot be blank'}, status=HTTP_400_BAD_REQUEST)
            if not member_id:
                return Response({'success': False,'message': 'Member field shouldnot be blank'}, status=HTTP_400_BAD_REQUEST)
            if not description:
                return Response({'success': False,'message': 'Description field shouldnot be blank'}, status=HTTP_400_BAD_REQUEST)
            # if not title:
            #     return Response({'success': False,'message': 'Title field shouldnot be blank'}, status=HTTP_400_BAD_REQUEST)
            if prayer_group_id and member_id and family_id and description:
                try:
                    prayer_group_id=PrayerGroup.objects.get(id=prayer_group_id)
                except:
                    return Response({'success': False,'message': 'Prayer Group doesnot exist'}, status=HTTP_400_BAD_REQUEST)
                try:
                    family_id=Family.objects.get(id=family_id)
                except:
                    return Response({'success': False,'message': 'Family doesnot exist'}, status=HTTP_400_BAD_REQUEST)

                if user_type=='SECONDARY':
                    try:
                        member_id=Members.objects.get(secondary_user_id=member_id)
                    except:
                        return Response({'success': False,'message': 'Member doesnot exist'}, status=HTTP_400_BAD_REQUEST)
                    beri_obj=NoticeBereavement.objects.create(prayer_group=prayer_group_id,family=family_id,secondary_member=member_id,description=description)
                    member_id.in_memory=True
                    member_id.in_memory_date=tz.now()
                    member_id.save()

                    # body = {
                    #     "type": "Bereavement",
                    #     "id": str(beri_obj.id),
                    #     "message": "Admin created one new Bereavement",
                    # }
                    try:
                        if member_id.primary_user_id.get_file_upload.first():
                            family_name = member_id.primary_user_id.get_file_upload.first().name
                        else:
                            family_name = ''

                        if family_name:
                            body = {"message":"Funeral announcement of %s belonging to %s"%(member_id.member_name,family_name),
                            "user_type": "SECONDARY",
                            "type":"bereavement",
                            "id":str(beri_obj.id)
                            }
                        else:
                            body = {"message":"Funeral announcement of %s"%(member_id.member_name),
                            "user_type": "SECONDARY",
                            "type":"bereavement",
                            "id":str(beri_obj.id)
                            }
                        notifications=Notification.objects.create(created_time=tz.now(),message=body)
                        primary_members=FileUpload.objects.all()
                        secondary_members=Members.objects.all()
                        for primary_member in primary_members:
                            NoticeReadPrimary.objects.create(notification=notifications,user_to=primary_member,is_read=False)
                        for secondary_member in secondary_members:
                            NoticeReadSecondary.objects.create(notification=notifications,user_to=secondary_member,is_read=False)
                    
                        try:
                            image= request.build_absolute_uri(member_id.image.url)
                        except:
                            image = ""
                        try:
                            content = {'title':'notice title','message':{"data":{"title":"Funeral Notice","body":"Funeral announcement of %s belonging to %s"%(member_id.member_name,family_name),"notificationType":"funeral","backgroundImage":image,"text_type":"long"},\
                            "notification":{"alert":"This is a FCM notification","title":"Funeral Notice","body":"Funeral announcement of %s belonging to %s"%(member_id.member_name,family_name),"sound":"default","backgroundImage":image,"backgroundImageTextColour":"#FFFFFF","image":image,"click_action":"notice"}} } 
                        
                            content_ios = {'message':{"aps":{"alert":{"title":"Funeral Notice","subtitle":"","body":"Funeral announcement of %s belonging to %s"%(member_id.member_name,family_name)},"sound":"default","category":"notice","badge":1,"mutable-content":1},"media-url":image}}
                            resp = fcm_messaging_to_all(content)
                            resp1 = apns_messaging_to_all(content_ios)
                        except:
                            pass
                    except:
                        pass
                    return Response({'success': True,'message':'Notice Created Successfully'}, status=HTTP_201_CREATED)
                else:
                    try:
                        member_id=FileUpload.objects.get(primary_user_id=member_id)
                    except:
                        return Response({'success': False,'message': 'Member doesnot exist'}, status=HTTP_400_BAD_REQUEST)
                    beri_obj = NoticeBereavement.objects.create(prayer_group=prayer_group_id,family=family_id,primary_member=member_id,description=description)
                    member_id.in_memory=True
                    member_id.in_memory_date=tz.now()
                    member_id.save()
                    # body = {
                    #     "type": "Bereavement",
                    #     "id": str(beri_obj.id),
                    #     "message": "Admin created one new Bereavement",
                    # }
                    try:
                        if member_id.get_file_upload.first():
                            family_name = member_id.get_file_upload.first().name
                        else:
                            family_name = ''
                        if family_name :

                            body = {"message":"Funeral announcement of %s belonging to %s"%(member_id.name,family_name),
                            "user_type": "PRIMARY",
                            "type":"bereavement",
                            "id":str(beri_obj.id)
                            }
                        else:
                            body = {"message":"Funeral announcement of %s "%(member_id.name),
                            "user_type": "PRIMARY",
                            "type":"bereavement",
                            "id":str(beri_obj.id)
                            }
                        notifications=Notification.objects.create(created_time=tz.now(),message=body)
                        primary_members=FileUpload.objects.all()
                        secondary_members=Members.objects.all()
                        for primary_member in primary_members:
                            NoticeReadPrimary.objects.create(notification=notifications,user_to=primary_member,is_read=False)
                        for secondary_member in secondary_members:
                            NoticeReadSecondary.objects.create(notification=notifications,user_to=secondary_member,is_read=False)
                        try:
                            image= request.build_absolute_uri(member_id.image.url)
                        except:
                            image = ""
                        try:
                            content = {'title':'notice title','message':{"data":{"title":"Funeral Notice","body":"Funeral announcement of %s belonging to %s"%(member_id.name,family_name),"notificationType":"notice","backgroundImage":image,"text_type":"long"},\
                            "notification":{"alert":"This is a FCM notification","title":"Funeral Notice","body":"Funeral announcement of %s belonging to %s"%(member_id.name,family_name),"sound":"default","backgroundImage":image,"backgroundImageTextColour":"#FFFFFF","image":image,"click_action":"notice"}} } 
                            
                            content_ios = {'message':{"aps":{"alert":{"title":"Funeral Notice","subtitle":"","body":"Funeral announcement of %s belonging to %s"%(member_id.name,family_name)},"sound":"default","category":"notice","badge":1,"mutable-content":1},"media-url":image}}
                            resp = fcm_messaging_to_all(content)
                            resp1 = apns_messaging_to_all(content_ios)
                        except:
                            pass
                    except:
                        pass
                    return Response({'success': True,'message':'Notice Created Successfully'}, status=HTTP_201_CREATED)

class NoticeBereavementEdit(RetrieveUpdateAPIView):
    queryset = NoticeBereavement.objects.all()
    serializer_class = NoticeBereavementSerializer
    permission_classes = [IsAdminUser]


class NoticeBereavementDelete(DestroyAPIView):
    queryset = NoticeBereavement.objects.all()
    serializer_class = NoticeBereavementSerializer
    permission_classes = [IsAdminUser]


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            if instance.primary_member:
                instance.primary_member.in_memory = False
                instance.primary_member.save()
            elif instance.secondary_member:
                instance.secondary_member.in_memory = False
                instance.secondary_member.save()
            else:
                pass
        except:
            pass

        self.perform_destroy(instance)
        data = {
            'code': 200,
            'status': "OK",
        }
        data['response'] = "Successfully deleted"
        return Response(data)


class UserNoticeList(ListAPIView):
    queryset=Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes=[IsAuthenticated]

    def list(self, request, *args, **kwargs):
        context ={
            'request': request
        }

        queryset_normal_notice = NoticeSerializer(Notice.objects.all(), many=True, context=context).data
        queryset_bereavement_notice = NoticeBereavementSerializer(NoticeBereavement.objects.all(), many=True, context=context).data

        response = []
        response_bereavement = []
        not_type = None
        for notice in queryset_normal_notice:
            if notice['image'] == None and notice['video'] == None and notice['audio'] != None:
                not_type = 'audio'
            elif notice['image'] == None and notice['audio'] == None and notice['video'] != None:
                not_type = 'video'
            else:
                not_type = 'notice'
            new_data ={
                'id': notice['id'],
                'type': not_type,
                'notice' : notice['notice'],
                'description': notice['description'],
                'image': notice['image'],
                'audio': notice['audio'],
                'video': notice['video'],
                'created_at': notice['created_at'],
                'updated_at': notice['updated_at'],

            }

            response.append(new_data)

        for bereavement in queryset_bereavement_notice:
            prayer=PrayerGroup.objects.get(id=bereavement['prayer_group'])
            family=Family.objects.get(id=bereavement['family'])
            try:
                member=FileUpload.objects.get(primary_user_id=bereavement['primary_member'])
                if member.image:
                    image=request.build_absolute_uri(member.image.url)
                else:
                    image='null'
                import datetime as dt
                today = dt.datetime.now()
                new_data ={
                'id': bereavement['id'],
                'type': 'bereavement',
                # 'title' : bereavement['title'],
                'description': bereavement['description'],
                'prayer_group': prayer.name,
                'family': family.name,
                'name': member.name,
                'occupation':member.occupation,
                'current_year':today.year,
                'dob':member.dob,
                'image':image,
                'created_at': bereavement['created_at'],

                # 'secondary_member': member_name.member_name,
                }

            except:
                import datetime as dt
                today = dt.datetime.now()
                member_name=Members.objects.get(secondary_user_id=bereavement['secondary_member'])
                family=Family.objects.get(id=bereavement['family'])
                if member_name.image:
                    image=request.build_absolute_uri(member_name.image.url)
                else:
                    image='null'
                new_data ={
                'id': bereavement['id'],
                'type': 'bereavement',
                # 'title' : bereavement['title'],
                'description': bereavement['description'],
                'prayer_group': prayer.name,
                'family': family.name,
                # 'primary_member': member.name,
                'name': member_name.member_name,
                'image':image,
                'current_year':today.year,
                'dob':member_name.dob,
                'occupation':member_name.occupation,
                'created_at': bereavement['created_at'],

            }




            # response.append(new_data)



            response.append(new_data)


        response_query = sorted(response, key = lambda i: i.get('created_at')) 
        data={
            'code': 200,
            'status': "OK",
            'response': response

            }
        data['response'] = {
            'notices':response_query,
            'normal notice count':len(queryset_normal_notice),
            'bereavement notice count':len(queryset_bereavement_notice)

            }
        # data['response']['member_details'].insert(0)

        return Response(data)



class UpdateFamilyByPrimary(APIView):
    queryset = Family.objects.all()
    serializer_class = FamilyEditSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        user=self.request.user.username
        serializer = FamilyEditSerializer(data=request.data)
        if serializer.is_valid():
            # import pdb;pdb.set_trace()
            try:
                if FileUpload.objects.filter(Q(phone_no_primary=user)|Q(phone_no_secondary=user)).exists():
                    user_id_primary=FileUpload.objects.get(Q(phone_no_primary=user)|Q(phone_no_secondary=user))
                elif Members.objects.filter(Q(phone_no_secondary_user=user)|Q(phone_no_secondary_user_secondary=user)).exists():
                    mem_obj = Members.objects.get(Q(phone_no_secondary_user=user)|Q(phone_no_secondary_user_secondary=user))
                    user_id_primary = mem_obj.primary_user_id
                else:
                    return Response({'status': False,'message': 'No such Family'},status=HTTP_400_BAD_REQUEST)
            except:
               return Response({'status': False,'message': 'No such Family'},status=HTTP_400_BAD_REQUEST)
            else:
                try:
                    instance=Family.objects.get(primary_user_id__primary_user_id=user_id_primary.primary_user_id)
                except:
                    return Response({'status': False,'message': 'You dont have any family,Please update and do edit'},status=HTTP_400_BAD_REQUEST)
                else:
                    instance.about=serializer.data['about']
                    try:
                        if request.FILES.get('image'):
                            instance.image = request.FILES['image']
                    except:
                        pass
                    instance.save()
                    data = {
                        'status': True,
                        'message': 'Family Detail Updated Successfully'
                        }
                return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                    'status': False,
                    'message': 'Invalid Family Detail'
                    }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)



class UpdateMemberByPrimary(APIView):
    lookup_field = 'pk'
    queryset = Members.objects.all()
    serializer_class = MemberSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsPrimaryUserOrReadOnly]

    def post(self, request, *args, **kwargs):
        instance = Members.objects.get(pk=kwargs.get('pk'))

        if not instance.primary_user_id.phone_no_primary == request.user.username:
            data ={
                'status': False,
                'message': 'You have no permissoin to update this member'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


        context = {
            'request': request
        }

        serializer = MemberSerializer(instance, data=request.data, context=context)

        if serializer.is_valid():
            data = serializer.data
            data.pop('primary_user_id')
            data.pop('family_name')
            data.pop('user_type')

            primary_user = FileUpload.objects.get(phone_no_primary=request.user.username)

            unapproved_member = UnapprovedMember.objects.filter(edit_user=instance.pk)
            unapproved_member.delete()

            unapproved_member = UnapprovedMember.objects.create(**data)
            unapproved_member.primary_user_id = primary_user
            unapproved_member.edit_user = instance.pk
            unapproved_member.save()

            success_data = {
                'status': True,
                "message": "Member Updated Successfully"
            }
            success_data['response'] = serializer.data

            return Response(success_data, status=status.HTTP_201_CREATED)
            
        data = {
            'status': False
        }
        data['response'] = serializer.errors

        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class CreateUserByAdminView(APIView):
    serializer_class = UserByadminSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, AdminPermission]

    def post(self, request, format=None):

        serializer = UserByadminSerializer(data=request.data)

        if serializer.is_valid():

            family = Family.objects.get(pk=serializer.data['family'])
            
            if family.primary_user_id and not family.primary_user_id.in_memory and serializer.data['member_type'] in ['Primary', 'primary']:
                data = {
                    'status': False,
                    'message': 'Primary user already exists for this family'
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            if serializer.data['member_type'] in ['Primary', 'primary']:
                
                instance = FileUpload(
                    name=serializer.data['name'],
                    dob=serializer.data['dob'],
                    blood_group=serializer.data['blood_group'],
                    email=serializer.data['email'],
                    phone_no_primary=serializer.data['secondary_number'],
                    phone_no_secondary=serializer.data['secondary_number'],
                    occupation=serializer.data['occupation'],
                    marital_status=serializer.data['marital_status'],
                    marrige_date=serializer.data['marrige_date'],
                    about=serializer.data['about'],
                )
            else:
                if not family.primary_user_id:
                    data = {
                        'status': False,
                        'message': 'Create a primary user to add secondary users'
                    }
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)

                instance = Members(
                    member_name=serializer.data['name'],
                    dob=serializer.data['dob'],
                    blood_group=serializer.data['blood_group'],
                    email=serializer.data['email'],
                    phone_no_secondary_user=serializer.data['secondary_number'],
                    phone_no_secondary_user_secondary=serializer.data['secondary_number'],
                    occupation=serializer.data['occupation'],
                    marital_status=serializer.data['marital_status'],
                    marrige_date=serializer.data['marrige_date'],
                    about=serializer.data['about'],
                    relation=serializer.data['member_type']
                )

            if serializer.data['member_status'] == 'in_memory':
                instance.in_memory = True

            if request.FILES.get('image'):
                instance.image = request.FILES['image']

            instance.save()

            if serializer.data['family']:

                if serializer.data['member_type'] in ['Primary', 'primary']:
                    family.primary_user_id = instance

                else:
                    instance.primary_user_id  = family.primary_user_id
                    instance.save()

                family.save()


            if serializer.data['prayer_group']:
                prayer_group = PrayerGroup.objects.get(pk=serializer.data['prayer_group'])
                
                if serializer.data['member_type'] in ['Primary', 'primary']:
                    prayer_group.primary_user_id.add(instance)
                else:
                    prayer_group.primary_user_id.add(instance.primary_user_id)
                
                data ={
                    'id': instance.pk
                }
                data.update(serializer.data)

                response={
                    "status": True,
                    "message": "User Created by admin"
                }

                response['response'] = data

            return Response(response)

        data={
            'status': False,
        }
        data['response'] = serializer.errors

        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserByAdminView(APIView):
    serializer_class = UserByadminSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, AdminPermission]

    def post(self, request, pk=None, format=None):
        response_data = []



        serializer = UserByadminSerializer(data=request.data)

        if serializer.is_valid():

            prayer_group = PrayerGroup.objects.get(pk=serializer.data['prayer_group'])
            family = Family.objects.get(pk=serializer.data['family'])

            if serializer.data['member_type'] in ['Primary', 'primary']:
                instance = FileUpload.objects.get(pk=pk)

                instance.name = serializer.data['name']
                instance.dob = serializer.data['dob']
                instance.blood_group = serializer.data['blood_group']
                instance.email = serializer.data['email']
                instance.phone_no_primary = serializer.data['primary_number']
                instance.phone_no_secondary = serializer.data['secondary_number']
                instance.occupation = serializer.data['occupation']
                instance.marital_status = serializer.data['marital_status']
                instance.marrige_date = serializer.data['marrige_date']
                instance.about = serializer.data['about']
                instance.save()

                previous_groups = instance.get_file_upload_prayergroup.all()
                
                for group in previous_groups:
                    group.primary_user_id.remove(instance)
                
                prayer_group.primary_user_id.add(instance)

                for pre_family in instance.get_file_upload.all():
                    pre_family.primary_EachUserNotificationuser_id = None
                    pre_family.save()

                family.primary_user_id = instance
                family.save()

            else:
                if not family.primary_user_id in prayer_group.primary_user_id.all():
                    data = {
                        'status': False,
                        'message': 'Invalid prayer group for family'
                    }
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)

                instance = Members.objects.get(pk=pk)
                instance.member_name = serializer.data['name']
                instance.dob = serializer.data['dob']
                instance.blood_group = serializer.data['blood_group']
                instance.email = serializer.data['email']
                instance.phone_no_secondary_user = serializer.data['primary_number']
                instance.phone_no_secondary_user_secondary = serializer.data['secondary_number']
                instance.occupation = serializer.data['occupation']
                instance.marital_status = serializer.data['marital_status']
                instance.marrige_date = serializer.data['marrige_date']
                instance.about = serializer.data['about']
                instance.save()

                instance.primary_user_id = family.primary_user_id

                if instance.primary_user_id:
                    previous_groups = instance.primary_user_id.get_file_upload_prayergroup.all()
                    
                    for group in previous_groups:
                        group.primary_user_id.remove(instance.primary_user_id)

                    prayer_group = PrayerGroup.objects.get(pk=serializer.data['prayer_group'])
                    prayer_group.primary_user_id.add(instance.primary_user_id)


                instance.save()

            if serializer.data['member_status'] == 'in_memory':
                instance.in_memory = True

            if request.FILES.get('image'):
                instance.image = request.FILES['image']

            instance.save()

            data ={
                'id': instance.pk
            }
            data.update(serializer.data)
            response_data.append(data)




            response={
                "status": True,
                "message": "User Updated by admin",
                "response":response_data
            }

            # response['response'] = data

            return Response(response)

        data={
            'status': False,
        }
        data['response'] = serializer.errors

        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class AddFamilyByAdminView(APIView):
    serializer_class = FamilyByadminSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, AdminPermission]

    def post(self, request, pk=None, format=None):

        serializer = FamilyByadminSerializer(data=request.data)

        if serializer.is_valid():
            prayer_group = PrayerGroup.objects.get(pk=serializer.data['prayer_group'])
            family_name = serializer.data['family_name']

            instance = Family(name=family_name)
            
            if request.FILES.get('image'):
                instance.image = request.FILES['image']

            instance.save()
            prayer_group.family.add(instance.id)
            prayer_group.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        serializer = FamilyByadminSerializer(data=request.data)
        if serializer.is_valid():
            family_name = serializer.data['family_name']
            try:
                data = {
                    'code': 200,
                    'status': "OK",
                }
                instance = Family.objects.get(id=pk,name=family_name)

                if request.FILES.get('image'):
                    instance.image = request.FILES['image']
                try:
                    about = request.POST.get('about')
                    instance.about = about
                except:
                    pass
                try:
                    about = request.POST.get('status')
                    if about == 'active':
                        instance.members_length = 0
                    elif about == 'inactive':
                        instance.members_length = 1
                except:
                    pass
                instance.save()
                data['response'] = "Family successfully updated"
                return Response(data,status=status.HTTP_200_OK)
            except:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        try:
            # import pdb;pdb.set_trace()
            instance = Family.objects.get(id=pk)
            if instance:
                # instance.delete()
                instance.members_length = 1   # 1: inactive status of family
                instance.save()
                # try:
                #     if instance.primary_user_id :

                # except:
                #     pass
                data = {
                    'code': 200,
                    'status': "OK",
                }
                data['response'] = "Family deleted successfully"
                return Response(data,status=status.HTTP_200_OK)
        except:
            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

class EachUserNotification(APIView):
    serializer_class = NoticeSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user=request.user.username
        try:
            member=FileUpload.objects.get(phone_no_primary=user)
            notice_section=NoticeReadPrimary.objects.filter(user_to=member)
            notice_section.update(is_read=True)
            messages=PrimaryNotificationSerializer(notice_section, many=True)
        except:

            try:
                member=Members.objects.get(phone_no_secondary_user=user)
                notice_section=NoticeReadSecondary.objects.filter(user_to=member)
                notice_section.update(is_read=True)
                messages=SecondaryNotificationSerializer(notice_section, many=True)
            except:
                admin_profile = AdminProfile.objects.get(user=request.user)
                notice_section=NoticeReadAdmin.objects.filter(user_to=admin_profile)
                notice_section.update(is_read=True)

                messages = AdminNotificationSerializer(notice_section, many=True)
        # data={
        #     'notification':messages.data,
        #     'status': True,
        # }

        data ={
            "success": True,
            "code": 200,
        }
        # impoer pdb;pdb.set_trace()
        data_obj = []

        # count_msg = notice_section.count()
        # count_msg= count_msg -1
        for index, notif in enumerate(notice_section):
            beri_flag = False
            notice_flag = False
            status_beri_flag = False
            status_prim_flag = False
            change_prim_num_flag =  False
            sec_add_flag = False
            if notif.notification.is_json == True :
                dump_value = json.dumps(messages.data[index])
                v1 = json.loads(dump_value)
                data_str =v1['message']
                json_val = ast.literal_eval(data_str)
                json_load_obj = json.dumps(json_val)
                data_final=json.loads(json_load_obj)
                data_final.update({"type":"Number request notification"})
                # data_obj = data_final
                data_obj.append(data_final)
                # count_msg= count_msg -1

            else:
                try:
                    data_str = messages.data[index]['message']
                    json_val = ast.literal_eval(data_str)
                    json_load_obj = json.dumps(json_val)
                    data_final=json.loads(json_load_obj)
                    if data_final['type'] == 'bereavement' :
                        data_obj.append(data_final)
                        beri_flag = True
                    elif data_final['type'] == 'notice' :
                        data_obj.append(data_final)
                        notice_flag = True
                    elif data_final['type'] == 'status_change_after_beraevement':
                        data_obj.append(data_final)
                        status_beri_flag = True
                    elif data_final['type'] == 'status_change_primary_to_secondary':
                        data_obj.append(data_final)
                        status_prim_flag = True
                    elif data_final['type'] == 'number_change_primary':
                        data_obj.append(data_final)
                        change_prim_num_flag = True
                    elif data_final['type'] == 'primary_add_secondary':
                        data_obj.append(data_final)
                        sec_add_flag = True

                    else:
                        pass
                except:
                    pass
                if not (beri_flag or notice_flag or status_beri_flag or status_prim_flag or change_prim_num_flag or sec_add_flag):
                    messages.data[index].update({"type":"Default notification"})
                    data_obj.append(messages.data[index])
        data['response'] = data_obj
        return Response(data,status=HTTP_200_OK)


class ViewRequestNumberViewset(CreateAPIView):
    queryset = ViewRequestNumber.objects.all()
    serializer_class = ViewRequestNumberSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request_from = request.POST.get('request_from', False)
        request_to = request.POST.get('request_to', False)

        usertype_from = request.POST.get('usertype_from', False)
        usertype_to = request.POST.get('usertype_to', False)
        if not request_from and not request_to and not  usertype_from and not usertype_to:
            return Response({'success': False,'message': 'You should fill all the fields'}, status=HTTP_400_BAD_REQUEST)
        else :
            try:
                if usertype_from == 'PRIMARY' :
                    if FileUpload.objects.filter(primary_user_id=request_from).exists():
                        if usertype_to == 'PRIMARY':

                            primary_user = FileUpload.objects.get(primary_user_id=request_to)
                            if primary_user:
                                ViewRequestNumber.objects.get_or_create(request_from=request_from,request_to=primary_user.primary_user_id,usertype_from='PRIMARY',usertype_to='PRIMARY',request_mobile=primary_user.phone_no_primary)

                                if usertype_from=='PRIMARY':
                                    try:
                                        from_user = FileUpload.objects.get(phone_no_primary=request.user.username)
                                    except:
                                        from_user = FileUpload.objects.get(phone_no_secondary=request.user.username)

                                    user_details={

                                        "from_number":request.user.username,
                                        "from_id":from_user.primary_user_id,
                                        "from_usertype":'PRIMARY',
                                        "from_user":from_user.name,
                                        "to_user":primary_user.name,
                                        "to_number":primary_user.phone_no_primary,
                                        "to_id":primary_user.primary_user_id,
                                        "send_time":str(tz.now())
                                    }
                                    user_details_str=str(user_details)
                                    not_obj = Notification.objects.create(created_by_primary=primary_user,
                                                                          message=user_details_str,is_json=True)
                                    if not_obj:
                                        user_details.update({"notification_id":not_obj.id})
                                        not_obj.message = str(user_details)
                                        not_obj.save()
                                    NoticeReadPrimary.objects.create(notification=not_obj, user_to=primary_user)
                                else:
                                    try:
                                        from_user = Members.objects.get(phone_no_secondary_user=request.user.username)
                                    except:
                                        from_user = Members.objects.get(phone_no_secondary_user_secondary=request.user.username)
                                    user_details = {

                                        "from_number": request.user.username,
                                        "from_id": from_user.secondary_user_id,
                                        "from_user": from_user.member_name,
                                        "from_usertype":'SECONDARY',
                                        "to_user": primary_user.name,
                                        "to_number": primary_user.phone_no_primary,
                                        "to_id": primary_user.primary_user_id,
                                        "send_time":str(tz.now())
                                    }

                                return Response({'success': True,'message':'Notification send Successfully','user_details':user_details}, status=HTTP_201_CREATED)
                        elif usertype_to == 'SECONDARY':
                            sec_user = Members.objects.get(secondary_user_id=request_to)
                            if sec_user:
                                # primary_user = FileUpload.objects.get(primary_user_id=request_to)
                                ViewRequestNumber.objects.get_or_create(request_from=request_from,request_to=sec_user.secondary_user_id,usertype_from='PRIMARY',usertype_to='SECONDARY',request_mobile=sec_user.phone_no_secondary_user)

                                if usertype_from == 'PRIMARY':
                                    try:
                                        from_user = FileUpload.objects.get(phone_no_primary=request.user.username)
                                    except:
                                        from_user = FileUpload.objects.get(phone_no_secondary=request.user.username)
                                    user_details = {

                                        "from_number": request.user.username,
                                        "from_id": from_user.primary_user_id,
                                        "from_user": from_user.name,
                                        "from_usertype":'PRIMARY',
                                        "to_user": sec_user.member_name,
                                        "to_number": sec_user.phone_no_secondary_user,
                                        "to_id": sec_user.secondary_user_id,
                                        "send_time":str(tz.now())
                                    }
                                    user_details_str=str(user_details)
                                    not_obj = Notification.objects.create(created_by_secondary=sec_user,
                                                                          message=user_details_str,is_json=True)
                                    if not_obj:
                                        user_details.update({"notification_id":not_obj.id})
                                        not_obj.message = str(user_details)
                                        not_obj.save()
                                    NoticeReadSecondary.objects.create(notification=not_obj, user_to=sec_user)
                                else:
                                    try:
                                        from_user = Members.objects.get(phone_no_secondary_user=request.user.username)
                                    except:
                                        from_user = Members.objects.get(
                                            phone_no_secondary_user_secondary=request.user.username)
                                    user_details = {

                                        "from_number": request.user.username,
                                        "from_id": from_user.secondary_user_id,
                                        "from_user": from_user.member_name,
                                        "from_usertype":'SECONDARY',
                                        "to_user": primary_user.name,
                                        "to_number": primary_user.phone_no_primary,
                                        "to_id": primary_user.primary_user_id,
                                        "send_time":str(tz.now())
                                    }

                                return Response({'success': True,'message':'Notification send Successfully','user_details':user_details}, status=HTTP_201_CREATED)
                        else:
                            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
                elif usertype_from == 'SECONDARY':
                    if Members.objects.filter(secondary_user_id=request_from).exists():
                        if usertype_to == 'PRIMARY':
                            primary_user = FileUpload.objects.get(primary_user_id=request_to)
                            if primary_user:
                                ViewRequestNumber.objects.get_or_create(request_from=request_from,request_to=primary_user.primary_user_id,usertype_from='SECONDARY',usertype_to='PRIMARY',request_mobile=primary_user.phone_no_primary)

                                if usertype_from == 'PRIMARY':
                                    try:
                                        from_user = FileUpload.objects.get(phone_no_primary=request.user.username)
                                    except:
                                        from_user = FileUpload.objects.get(phone_no_secondary=request.user.username)
                                    user_details = {

                                        "from_number": request.user.username,
                                        "from_id": from_user.primary_user_id,
                                        "from_user": from_user.name,
                                        "from_usertype":'PRIMARY',
                                        "to_user": primary_user.name,
                                        "to_number": primary_user.phone_no_primary,
                                        "to_id": primary_user.primary_user_id,
                                        "send_time":str(tz.now())
                                    }
                                else:
                                    try:
                                        from_user = Members.objects.get(phone_no_secondary_user=request.user.username)
                                    except:
                                        from_user = Members.objects.get(
                                            phone_no_secondary_user_secondary=request.user.username)
                                    user_details = {

                                        "from_number": request.user.username,
                                        "from_id": from_user.secondary_user_id,
                                        "from_user": from_user.member_name,
                                        "from_usertype":'SECONDARY',
                                        "to_user": primary_user.name,
                                        "to_number": primary_user.phone_no_primary,
                                        "to_id": primary_user.primary_user_id,
                                        "send_time":str(tz.now())
                                    }
                                    user_details_str = str(user_details)
                                    not_obj = Notification.objects.create(created_by_primary=primary_user,
                                                                          message=user_details_str,is_json=True)
                                    if not_obj:
                                        user_details.update({"notification_id":not_obj.id})
                                        not_obj.message = str(user_details)
                                        not_obj.save()
                                    NoticeReadPrimary.objects.create(notification=not_obj, user_to=primary_user)


                                return Response({'success': True,'message':'Notification send Successfully','user_details':user_details}, status=HTTP_201_CREATED)
                        elif usertype_to == 'SECONDARY':
                            sec_user = Members.objects.get(secondary_user_id=request_to)
                            if sec_user:
                                ViewRequestNumber.objects.get_or_create(request_from=request_from,request_to=sec_user.secondary_user_id,usertype_from='SECONDARY',usertype_to='SECONDARY',request_mobile=sec_user.phone_no_secondary_user)
                                # primary_user = FileUpload.objects.get(primary_user_id=request_to)
                                if usertype_from == 'PRIMARY':
                                    try:
                                        from_user = FileUpload.objects.get(phone_no_primary=request.user.username)
                                    except:
                                        from_user = FileUpload.objects.get(phone_no_secondary=request.user.username)
                                    user_details = {

                                        "from_number": request.user.username,
                                        "from_id": from_user.primary_user_id,
                                        "from_user": from_user.name,
                                        "from_usertype":'PRIMARY',
                                        "to_user": primary_user.name,
                                        "to_number": primary_user.phone_no_primary,
                                        "to_id": primary_user.primary_user_id,
                                        "send_time":str(tz.now())
                                    }
                                else:

                                    try:
                                        from_user = Members.objects.get(phone_no_secondary_user=request.user.username)
                                    except:
                                        from_user = Members.objects.get(
                                            phone_no_secondary_user_secondary=request.user.username)
                                    user_details = {

                                        "from_number": request.user.username,
                                        "from_id": from_user.secondary_user_id,
                                        "from_user": from_user.member_name,
                                        "from_usertype":'SECONDARY',
                                        "to_user": sec_user.member_name,
                                        "to_number": sec_user.phone_no_secondary_user,
                                        "to_id": sec_user.secondary_user_id,
                                        "send_time":str(tz.now())
                                    }
                                    user_details_str=str(user_details)
                                    not_obj = Notification.objects.create(created_by_secondary=sec_user,
                                                                          message=user_details_str,is_json=True)
                                    if not_obj:
                                        user_details.update({"notification_id":not_obj.id})
                                        not_obj.message = str(user_details)
                                        not_obj.save()
                                    NoticeReadSecondary.objects.create(notification=not_obj, user_to=sec_user)
                                return Response({'success': True,'message':'Notification send Successfully','user_details':user_details}, status=HTTP_201_CREATED)
                        else:
                            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({'success': False,'message': 'Something Went Wrong'}, status=status.HTTP_400_BAD_REQUEST)
                

class AcceptViewRequestNumberViewset(CreateAPIView):
    queryset = ViewRequestNumber.objects.all()
    serializer_class = RequestAcceptNumberSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
      
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_from = serializer.validated_data.get("request_from", None)
        request_to = serializer.validated_data.get("request_to", None)
        usertype_from = serializer.validated_data.get("usertype_from", None)
        usertype_to = serializer.validated_data.get("usertype_to", None)
        is_accepted = serializer.validated_data.get("is_accepted", None)


        if not request_from and not request_to and not  usertype_from and not usertype_to and not is_accepted :
            return Response({'success': False,'message': 'You should fill all the fields'}, status=HTTP_400_BAD_REQUEST)
        else :
            try:
                if is_accepted == True:
                    try:
                        obj = ViewRequestNumber.objects.get(request_from=request_from,request_to=request_to,usertype_from=usertype_from,usertype_to=usertype_to)
                    except:
                        obj = None
                    if obj:
                        obj.is_accepted=True
                        obj.save()
                        try:
                            if usertype_from == 'PRIMARY':
                                if usertype_to == 'PRIMARY' :
                                    prim_obj = FileUpload.objects.get(primary_user_id =int(request_to))
                                    user_details_str = "Number request accepted by %s"%(prim_obj.name)
                                    prim_obj_not = FileUpload.objects.get(primary_user_id =int(request_from))
                                    not_obj = Notification.objects.create(created_by_primary=prim_obj_not,
                                                                                  message=user_details_str)
                                    NoticeReadPrimary.objects.create(notification=not_obj, user_to=prim_obj_not)
                                    not_obj.save()
                                elif usertype_to == 'SECONDARY':
                                    sec_obj = Members.objects.get(secondary_user_id =int(request_to))
                                    user_details_str = "Number request accepted by %s"%(sec_obj.member_name)
                                    prim_obj_not = FileUpload.objects.get(primary_user_id =int(request_from))
                                    not_obj = Notification.objects.create(created_by_primary=prim_obj_not,
                                                                                  message=user_details_str)

                                    NoticeReadPrimary.objects.create(notification=not_obj, user_to=prim_obj_not)
                                    not_obj.save()

                            elif usertype_from == 'SECONDARY':
                                if usertype_to == 'PRIMARY' :
                                    prim_obj = FileUpload.objects.get(primary_user_id =int(request_to))
                                    user_details_str = "Number request accepted by %s"%(prim_obj.name)
                                    sec_obj_not = Members.objects.get(secondary_user_id =int(request_from))
                                    not_obj = Notification.objects.create(created_by_secondary=sec_obj_not,
                                                                                  message=user_details_str)

                                    NoticeReadPrimary.objects.create(notification=not_obj, user_to=sec_obj_not)
                                    not_obj.save()
                                elif usertype_to == 'SECONDARY':
                                    sec_obj = Members.objects.get(secondary_user_id =int(request_to))
                                    user_details_str = "Number request accepted by %s"%(sec_obj.member_name)
                                    sec_obj_not = Members.objects.get(secondary_user_id =int(request_from))
                                    not_obj = Notification.objects.create(created_by_secondary=sec_obj_not,message=user_details_str)

                                    NoticeReadSecondary.objects.create(notification=not_obj, user_to=sec_obj_not)
                                    not_obj.save()
                        except:
                            pass
                        
                    
                    return Response({'success': True,'message':'Phone number access accepted'}, status=HTTP_201_CREATED)

                else :
                    try:
                        obj = ViewRequestNumber.objects.get(request_from=request_from,request_to=request_to,usertype_from=usertype_from,usertype_to=usertype_to)
                    except:
                        obj = None
                    if obj:
                        obj.is_accepted=False
                        obj.request_mobile = ''
                        obj.save()

                    return Response({'success': True,'message':'Phone number access rejected'}, status=HTTP_201_CREATED)
  
            except:
                return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)



class EachUserUnreadCount(APIView):
    serializer_class = NoticeSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user=request.user.username
        data ={
            "success": True,
            "code": 200,
        }
        try:
            member=FileUpload.objects.get(phone_no_primary=user)
            notice_read_section=NoticeReadPrimary.objects.filter(user_to=member,is_read=True)
            notice_unread_section=NoticeReadPrimary.objects.filter(user_to=member,is_read=False)
            count_read=len(notice_read_section)
            count_unread=len(notice_unread_section)
        except:
            try:
                member=Members.objects.get(phone_no_secondary_user=user)
                notice_read_section=NoticeReadSecondary.objects.filter(user_to=member,is_read=True)
                notice_unread_section=NoticeReadSecondary.objects.filter(user_to=member,is_read=False)
                count_read=len(notice_read_section)
                count_unread=len(notice_unread_section)
            except:
                
                admin_profile = AdminProfile.objects.get(user=request.user)
                notice_read_section=NoticeReadAdmin.objects.filter(user_to=admin_profile,is_read=True)
                notice_unread_section=NoticeReadAdmin.objects.filter(user_to=admin_profile,is_read=False)
                count_read=len(notice_read_section)
                count_unread=len(notice_unread_section)



        data['response']={
            'Unreadcount':count_unread,
            'Readcount':count_read,
            'status': True,
        }
        return Response(data,status=HTTP_200_OK)

class PrivacyView(TemplateView):
    template_name = 'Privacy/privacy.html'

    def get_context_data(self, **kwargs):
        context = super(PrivacyView, self).get_context_data(**kwargs)
        context['privacy']= PrivacyPolicy.objects.first().policy
        return context


class PhoneVersionView(ModelViewSet):
    queryset = PhoneVersion.objects.all()
    serializer_class = PhoneVersionSerializer
    permission_classes = [AllowAny]

class GalleryImagesView(ModelViewSet):
    queryset = Images.objects.all()
    serializer_class = GalleryImagesSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        data = {
                'code': 200,
                'status': "OK",
        }
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        data['response'] = serializer.data
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = {
            'code': 200,
            'status': "OK",
        }
        data['response'] = serializer.data
        return Response(data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = {
            'code': 200,
            'status': "OK",
        }
        data['response'] = serializer.data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        data = {
            'code': 200,
            'status': "OK",
        }
        data['response'] = "Successfully deleted"
        return Response(data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = {
            'code': 200,
            'status': "OK",
        }
        data['response'] = serializer.data
        return Response(data)


class GalleryImagesCreateView(ModelViewSet):
    queryset = Images.objects.all()
    serializer_class = GalleryImagesSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(date=tz.now().date())

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        data = {
            'code': 200,
            'status': "OK",
        }
        data['response'] = serializer.data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        data = {
            'code': 200,
            'status': "OK",
        }
        data['response'] = "Successfully deleted"
        return Response(data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = {
            'code': 200,
            'status': "OK",
        }
        data['response'] = serializer.data
        return Response(data)

class UserListView(ListAPIView):
    queryset = FileUpload.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):

        context ={
            'request': request
        }
        
        queryset_primary = PrimaryUserSerializer(FileUpload.objects.all().order_by('name'), many=True, context=context).data
        queryset_secondary = MemberSerializer(Members.objects.all().order_by('member_name'), many=True, context=context).data

        response = []
        for primary in queryset_primary:

            new_data ={
                'user_id' : primary['primary_user_id'],
                'name': primary['name'],
                'image': primary['image'],
                'address': primary['address'],
                'phone_no_primary': primary['phone_no_primary'],
                'phone_no_secondary': primary['phone_no_secondary'],
                'dob': primary['dob'],
                'dom': primary['dom'],
                'blood_group': primary['blood_group'],
                'email': primary['email'],
                'occupation': primary['occupation'],
                'about': primary['about'],
                'marital_status': primary['marital_status'],
                'in_memory': primary['in_memory'],
                'in_memory_date': primary['in_memory_date'],
                'family_name': primary['family_name'],
                'user_type': primary['user_type']
            }

            response.append(new_data)

        for secondary in queryset_secondary:

            new_data ={
                'user_id' : secondary['secondary_user_id'],
                'name': secondary['member_name'],
                'image': secondary['image'],
                'phone_no_primary': secondary['phone_no_secondary_user'],
                'phone_no_secondary': secondary['phone_no_secondary_user_secondary'],
                'dob': secondary['dob'],
                'dom': secondary['dom'],
                'blood_group': secondary['blood_group'],
                'email': secondary['email'],
                'occupation': secondary['occupation'],
                'about': secondary['about'],
                'marital_status': secondary['marital_status'],
                'in_memory': secondary['in_memory'],
                'in_memory_date': secondary['in_memory_date'],
                'family_name': secondary['family_name'],
                'user_type': secondary['user_type'],
                'relation': secondary['relation'],
                'primary_user_id': secondary['primary_user_id']
            }

            response.append(new_data)


        data={
            'code': 200,
            'status': "OK",
            'response': response

            }

        return Response(data)

class FamilyListPaginatedView(ListAPIView):
    queryset = Family.objects.all().order_by('name')
    serializer_class = FamilyListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    def list(self, request, *args, **kwargs):
        try:
            term = request.GET['term']
            if term:
                term = term.replace(" ", "")
                term.lower()
                queryset = Family.objects.filter(name__nospaces__icontains=term).order_by('name')
            else:
                queryset = self.filter_queryset(self.get_queryset())
        except:
            queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            data = {
                'code': 200,
                'status': "OK",
            }

            page_nated_data = self.get_paginated_response(serializer.data).data
            data.update(page_nated_data)
            data['response'] = data.pop('results')

            return Response(data)


        serializer = self.get_serializer(queryset, many=True)

        data = {
            'code': 200,
            'status': "OK",
            'response': serializer.data
        }

        return Response(data)

class PrayerGroupBasedFamilyPaginatedView(ListAPIView):
    queryset = Family.objects.all()
    serializer_class = FamilyListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self, *args, **kwargs):
        prayer_id = self.kwargs['pk']
        
        try:
            prayer_group = PrayerGroup.objects.get(id=prayer_id)
        except PrayerGroup.DoesNotExist:
            raise exceptions.NotFound(detail="Prayer group does not exist")
        family_list1 = prayer_group.family.all().order_by('name')
        family_list1 = family_list1.filter(primary_user_id=None)
        family_list2 = Family.objects.filter(primary_user_id__in=prayer_group.primary_user_id.all())
        family_list = family_list1 | family_list2
        return family_list

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            term = request.GET['term']
            if term:
                term = term.replace(" ", "")
                term.lower()
                queryset = queryset.filter(name__nospaces__icontains=term).order_by('name')
            else:
                queryset = self.filter_queryset(self.get_queryset())
        except:
            queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            data = {
                'code': 200,
                'status': "OK",
            }

            page_nated_data = self.get_paginated_response(serializer.data).data
            data.update(page_nated_data)
            data['response'] = data.pop('results')

            return Response(data)


        serializer = self.get_serializer(queryset, many=True)

        data = {
            'code': 200,
            'status': "OK",
            'response': serializer.data
        }

        return Response(data)


class PrayerGroupBasedMembersPaginatedView(ListAPIView):
    queryset = PrayerGroup.objects.all()
    serializer_class = MembersSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self, *args, **kwargs):
        prayer_id = self.kwargs['pk']

        try:
            prayer_group = PrayerGroup.objects.get(id=prayer_id)
        except PrayerGroup.DoesNotExist:
            raise exceptions.NotFound(detail="Prayer group does not exist")
        self.primary_user = prayer_group.primary_user_id
        member_list = Members.objects.filter(primary_user_id__in=prayer_group.primary_user_id.all()).order_by('member_name')
        return member_list

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        term = None
        try:
            term = request.GET['term']
            if term:
                term = term.replace(" ", "")
                term.lower()
                queryset = queryset.filter(Q(member_name__nospaces__icontains=term)|Q(occupation__icontains=term)).order_by('member_name')
                queryset_primary = self.primary_user.filter(Q(name__nospaces__icontains=term)|Q(occupation__icontains=term))
            else:
                queryset = self.filter_queryset(self.get_queryset())
                queryset_primary = self.primary_user.all()
        except:
            queryset = self.filter_queryset(self.get_queryset())
            queryset_primary = self.primary_user.all()
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)

        #     data = {
        #         'code': 200,
        #         'status': "OK",
        #     }

        #     page_nated_data = self.get_paginated_response(serializer.data).data
        #     data.update(page_nated_data)
        #      response = data.pop('results')
        #     # return Response(data)
        serializer = self.get_serializer(queryset, many=True)

        # data = {
        #     'code': 200,
        #     'status': "OK",
        #     'response': serializer.data
        # }
        response = serializer.data
        for primary_user in queryset_primary:
            primary_user_id = UserRetrieveSerializer(primary_user,context={'request':request}).data

            response.insert(0, primary_user_id)

        if term:
            res = sorted([x for x in response if (x['name'].replace(" ","").lower()).startswith(term.lower())], key = lambda i: i['name'])
            names = list(map(itemgetter('name'), res)) 
            response_query = res + sorted([x for x in response if x['name'] not in names], key = lambda i: i['name'])
        else:
            response_query = sorted(response, key = lambda i: i['name']) 
            
        page = self.paginate_queryset(response_query)
        if page is not None:
            # serializer = CommonUserSerializer(responses,many=True)
            data = {
                'code': 200,
                'status': "OK",
            }
            page_nated_data = self.get_paginated_response(page).data
            data.update(page_nated_data)
        data['response'] = response_query
        data['response'] = data.pop('results')
        return Response(data)


class UpdatePhoneNumberSecondary(APIView):
    queryset = Members.objects.all()
    serializer_class = MemberNumberSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # import pdb;pdb.set_trace()
        # instance=Members.objects.get(phone_no_secondary_user=request.user.username)
        serializer = MemberNumberSerializer(data=request.data)

        if serializer.is_valid():
            phone_number = serializer.data.get('phone_no_secondary_user',None)
            phone_number_sec = serializer.data.get('phone_no_secondary_user_secondary',None)
            if phone_number :
                if FileUpload.objects.filter(phone_no_primary=phone_number).exists() or \
                    FileUpload.objects.filter(phone_no_secondary=phone_number).exists()  or \
                    Members.objects.filter(phone_no_secondary_user=phone_number).exists() or\
                    Members.objects.filter(phone_no_secondary_user_secondary=phone_number).exists() :
               
                    data = {
                        'status': False,
                        'message':"This phone number already registered.Please use another number"
                    }
                    data['response'] = serializer.errors

                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                try:
                    member=Members.objects.get(phone_no_secondary_user=request.user.username)
                    member.phone_no_secondary_user = phone_number
                    member.save()
                    user,created=User.objects.get_or_create(username=phone_number)
                    token, created = Token.objects.get_or_create(user=user)
                    data1 = {
                            'mobile': phone_number,
                            'user_type': 'SECONDARY',
                            'name': member.member_name,
                            'token':token.key,
                            'user_id':member.secondary_user_id
                    }
                    # request.user.auth_token.delete()
                except:
                    data = {
                        'status': False,
                        'message':"You have no permission to do this action"
                    }
                    data['response'] = serializer.errors

                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                success_data = {
                    'status': True,
                    "message": "Member Phone number Updated Successfully"
                }
                success_data.update(serializer.data)
                data1.update(success_data)
                success_data['response'] = data1
                # success_data['user_details'] = data1

                return Response(success_data, status=status.HTTP_201_CREATED)
            elif phone_number_sec:
                if FileUpload.objects.filter(phone_no_primary=phone_number_sec).exists() or \
                    FileUpload.objects.filter(phone_no_secondary=phone_number_sec).exists()  or \
                    Members.objects.filter(phone_no_secondary_user=phone_number_sec).exists() or\
                    Members.objects.filter(phone_no_secondary_user_secondary=phone_number_sec).exists() :
               
                    data = {
                        'status': False,
                        'message':"Phone number already registered"
                    }
                    data['response'] = serializer.errors

                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                try:
                    member=Members.objects.get(phone_no_secondary_user=request.user.username)
                    member.phone_no_secondary_user_secondary = phone_number_sec
                    member.save()
                    user,created=User.objects.get_or_create(username=phone_number_sec)
                    token, created = Token.objects.get_or_create(user=user)
                    data1 = {
                            'mobile': phone_number_sec,
                            'user_type': 'SECONDARY',
                            'name': member.member_name,
                            'token':token.key,
                            'user_id':member.secondary_user_id
                    }
                    # request.user.auth_token.delete()
                except:
                    data = {
                        'status': False,
                        'message':"You have no permission to do this action"
                    }
                    data['response'] = serializer.errors

                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                success_data = {
                    'status': True,
                    "message": "Member Phone number Updated Successfully"
                }
                success_data.update(serializer.data)
                data1.update(success_data)
                success_data['response'] = data1
                # success_data['user_details'] = data1
                return Response(success_data, status=status.HTTP_201_CREATED)
            else:
                pass

            
        data = {
            'status': False
        }
        data['response'] = serializer.errors

        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class PrimaryToSecondaryViewset(CreateAPIView):
    queryset = PrimaryToSecondary.objects.all()
    serializer_class = PrimaryToSecondarySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request_from = request.POST.get('request_from', False)
        request_to = request.POST.get('request_to', False)
        usertype_from = request.POST.get('usertype_from', False)
        if not request_from and not request_to and not  usertype_from :
            return Response({'success': False,'message': 'You should fill all the fields'}, status=HTTP_400_BAD_REQUEST)
        else :
            try:
                if usertype_from == 'PRIMARY' :
                    if FileUpload.objects.filter(primary_user_id=int(request_from)).exists():
                        primary_user = FileUpload.objects.get(primary_user_id=request_from)
                        sec_user = Members.objects.get(secondary_user_id=request_to)
                        # import pdb;pdb.set_trace()
                        if primary_user.primary_user_id == sec_user.primary_user_id.primary_user_id:
                            if PrimaryToSecondary.objects.filter(request_from=request_from,request_to=sec_user.secondary_user_id,usertype_from='PRIMARY',status=None).exists():
                                data = {
                                    'status': False,
                                    'message':"You are already requested for status change"
                                }
                                data['response'] = {}

                                return Response(data, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                obj = PrimaryToSecondary.objects.create(request_from=request_from,request_to=sec_user.secondary_user_id,usertype_from='PRIMARY')
                                try:
                                    from_user = FileUpload.objects.get(phone_no_primary=request.user.username)
                                except:
                                    from_user = FileUpload.objects.get(phone_no_secondary=request.user.username)

                                user_details={
                                    "notification_id":obj.id,
                                    "from_id":from_user.primary_user_id,
                                    "from_usertype":'PRIMARY',
                                    "from_user":from_user.name,
                                    "from_phone_number":from_user.phone_no_primary,
                                    "to_user":sec_user.member_name,
                                    "to_id":sec_user.secondary_user_id,
                                    "family_name":from_user.get_file_upload.first().name,
                                    "prayer_group_name":from_user.get_file_upload_prayergroup.first().name,
                                    "send_time":str(tz.now()),
                                    "type":"status_change_primary_to_secondary",
                                }

                                user_details_str=str(user_details)
                                notification = Notification.objects.create(
                                    created_by_primary=primary_user, 
                                    message=user_details_str
                                )

                                admin_profiles = AdminProfile.objects.all()

                                for admin_profile in admin_profiles:
                                    NoticeReadAdmin.objects.create(notification=notification, user_to=admin_profile)
                                

                                success_data = {
                                    'status': True,
                                    "message": "Status change request is send successfully.Wait admin to approve/reject"
                                }
                                success_data['response'] = user_details
                                return Response(success_data, status=status.HTTP_201_CREATED)
                        else:

                            data = {
                                'status': False,
                                'message':"You have no permission to do this action"
                            }
                            data['response'] = {}

                            return Response(data, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        data = {
                            'status': False,
                            'message':"Primary member doesnot exist"
                        }
                        data['response'] = {}

                        return Response(data, status=status.HTTP_400_BAD_REQUEST)

                elif usertype_from == 'SECONDARY' :

                    if Members.objects.filter(secondary_user_id=int(request_from)).exists():
                        primary_user = FileUpload.objects.get(primary_user_id=request_to)
                        sec_user = Members.objects.get(secondary_user_id=request_from)
                        if primary_user.in_memory == True :
                            if primary_user.primary_user_id == sec_user.primary_user_id.primary_user_id:
                                if PrimaryToSecondary.objects.filter(request_from=request_from,request_to=primary_user.primary_user_id,usertype_from='SECONDARY',status=None).exists():
                                    data = {
                                        'status': False,
                                        'message':"You are already requested for status change"
                                    }
                                    data['response'] = {}

                                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                                else:
                                    obj=PrimaryToSecondary.objects.create(request_from=request_from,request_to=primary_user.primary_user_id,usertype_from='SECONDARY')
                                    try:
                                        from_user = Members.objects.get(phone_no_secondary_user=request.user.username)
                                        if from_user.phone_no_secondary_user:
                                            from_user_phone = from_user.phone_no_secondary_user
                                        else:
                                            from_user_phone = None
                                    except:
                                        from_user = Members.objects.get(phone_no_secondary_user_secondary=request.user.username)
                                        if from_user.phone_no_secondary_user_secondary:
                                            from_user_phone = from_user.phone_no_secondary_user_secondary
                                        else:
                                            from_user_phone = None
                                    user_details={
                                        "notification_id":obj.id,
                                        "from_id":from_user.secondary_user_id,
                                        "from_usertype":'SECONDARY',
                                        "from_user":from_user.member_name,
                                        "from_phone_number":from_user_phone,
                                        "to_user":primary_user.name,
                                        "to_id":primary_user.primary_user_id,
                                        "family_name":primary_user.get_file_upload.first().name,
                                        "prayer_group_name":primary_user.get_file_upload_prayergroup.first().name,
                                        "send_time":str(tz.now()),
                                        "type":"status_change_after_beraevement",
                                    }

                                    user_details_str=str(user_details)
                                    notification = Notification.objects.create(
                                        created_by_secondary=sec_user, 
                                        message=user_details_str
                                    )

                                    admin_profiles = AdminProfile.objects.all()

                                    for admin_profile in admin_profiles:
                                        NoticeReadAdmin.objects.create(notification=notification, user_to=admin_profile)
                                    

                                    success_data = {
                                        'status': True,
                                        "message": "Status change request is send successfully.Wait admin to approve/reject"
                                    }
                                    success_data['response'] = user_details
                                    return Response(success_data, status=status.HTTP_201_CREATED)
                            else:

                                data = {
                                    'status': False,
                                    'message':"You have no permission to do this action"
                                }
                                data['response'] = {}

                                return Response(data, status=status.HTTP_400_BAD_REQUEST)
                        else:        
                            data = {
                                'status': False,
                                'message':"You have no permission to do this action"
                            }
                            data['response'] = {}

                            return Response(data, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        data = {
                            'status': False,
                            'message':"Member doesnot exist"
                        }
                        data['response'] = serializer.errors

                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({'success': False,'message': 'Something Went Wrong'}, status=status.HTTP_400_BAD_REQUEST)
                
class StatusChangeAcceptView(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    queryset = PrimaryToSecondary.objects.all()
    serializer_class = PrimaryToSecondarySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        data ={
            "success": True,
            "code": 200,
        }

        data['response'] = serializer.data

        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        data ={
            "success": True,
            "code": 200,
        }

        data['response'] = serializer.data

        return Response(data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        data ={
            "success": True,
            "code": 200,
        }

        data['response'] = serializer.data

        return Response(data)

    @action(methods=['get'], detail=True, url_path='approve-primary',
        permission_classes=[IsAuthenticated, AdminPermission])
    def approve_primary(self, request, pk=None):
        # import pdb;pdb.set_trace()
        member = self.get_object()
        if member:
            try:  
                if member.usertype_from == 'PRIMARY':
                    prim_obj = FileUpload.objects.get(primary_user_id = int(member.request_from))
                    sec_obj = Members.objects.get(secondary_user_id = int(member.request_to))
                    if prim_obj and sec_obj:

                        name1 = sec_obj.member_name
                        sec_obj.member_name = prim_obj.name
                        prim_obj.name = name1

                        image1 = sec_obj.image
                        sec_obj.image = prim_obj.image
                        prim_obj.image = image1

                        # address1 = sec_obj.address
                        # sec_obj.address = prim_obj.address
                        # prim_obj.address = address1

                        phone1 = sec_obj.phone_no_secondary_user
                        sec_obj.phone_no_secondary_user = prim_obj.phone_no_primary
                        prim_obj.phone_no_primary = phone1

                        phone2 = sec_obj.phone_no_secondary_user_secondary
                        sec_obj.phone_no_secondary_user_secondary = prim_obj.phone_no_secondary
                        prim_obj.phone_no_secondary = phone2

                        dob1 = sec_obj.dob
                        sec_obj.dob = prim_obj.dob
                        prim_obj.dob = dob1

                        dom1= sec_obj.dom
                        sec_obj.dom = prim_obj.dom
                        prim_obj.dom = dom1

                        blood_group1= sec_obj.blood_group
                        sec_obj.blood_group = prim_obj.blood_group
                        prim_obj.blood_group = blood_group1

                        email1= sec_obj.email
                        sec_obj.email = prim_obj.email
                        prim_obj.email = email1

                        occupation1= sec_obj.occupation
                        sec_obj.occupation = prim_obj.occupation
                        prim_obj.occupation = occupation1

                        about1= sec_obj.about
                        sec_obj.about = prim_obj.about
                        prim_obj.about = about1

                        marital_status1= sec_obj.marital_status
                        sec_obj.marital_status = prim_obj.marital_status
                        prim_obj.marital_status = marital_status1

                        marrige_date1= sec_obj.marrige_date
                        sec_obj.marrige_date = prim_obj.marrige_date
                        prim_obj.marrige_date = marrige_date1

                        in_memory1= sec_obj.in_memory
                        sec_obj.in_memory = prim_obj.in_memory
                        prim_obj.in_memory = in_memory1

                        in_memory_date1= sec_obj.in_memory_date
                        sec_obj.in_memory_date = prim_obj.in_memory_date
                        prim_obj.in_memory_date= in_memory_date1

                        relation1= sec_obj.relation
                        sec_obj.relation = prim_obj.relation
                        prim_obj.relation= relation1

                        try:
                            temp_num = prim_obj.phone_no_primary
                            token_obj = Token.objects.get(user__username=temp_num)
                            token_obj.delete()
                        except:
                            temp_num = sec_obj.phone_no_secondary_user
                            token_obj = Token.objects.get(user__username=temp_num)
                            token_obj.delete()
                        prim_obj.save()
                        sec_obj.save()

                elif member.usertype_from == 'SECONDARY':
                    prim_obj = FileUpload.objects.get(primary_user_id = int(member.request_to))
                    sec_obj = Members.objects.get(secondary_user_id = int(member.request_from))
                    if prim_obj and sec_obj:

                        name1 = sec_obj.member_name
                        sec_obj.member_name = prim_obj.name
                        prim_obj.name = name1

                        image1 = sec_obj.image
                        sec_obj.image = prim_obj.image
                        prim_obj.image = image1

                        # address1 = sec_obj.address
                        # sec_obj.address = prim_obj.address
                        # prim_obj.address = address1

                        phone1 = sec_obj.phone_no_secondary_user
                        sec_obj.phone_no_secondary_user = prim_obj.phone_no_primary
                        prim_obj.phone_no_primary = phone1

                        phone2 = sec_obj.phone_no_secondary_user_secondary
                        sec_obj.phone_no_secondary_user_secondary = prim_obj.phone_no_secondary
                        prim_obj.phone_no_secondary = phone2

                        dob1 = sec_obj.dob
                        sec_obj.dob = prim_obj.dob
                        prim_obj.dob = dob1

                        dom1= sec_obj.dom
                        sec_obj.dom = prim_obj.dom
                        prim_obj.dom = dom1

                        blood_group1= sec_obj.blood_group
                        sec_obj.blood_group = prim_obj.blood_group
                        prim_obj.blood_group = blood_group1

                        email1= sec_obj.email
                        sec_obj.email = prim_obj.email
                        prim_obj.email = email1

                        occupation1= sec_obj.occupation
                        sec_obj.occupation = prim_obj.occupation
                        prim_obj.occupation = occupation1

                        about1= sec_obj.about
                        sec_obj.about = prim_obj.about
                        prim_obj.about = about1

                        marital_status1= sec_obj.marital_status
                        sec_obj.marital_status = prim_obj.marital_status
                        prim_obj.marital_status = marital_status1

                        marrige_date1= sec_obj.marrige_date
                        sec_obj.marrige_date = prim_obj.marrige_date
                        prim_obj.marrige_date = marrige_date1

                        in_memory1= sec_obj.in_memory
                        sec_obj.in_memory = prim_obj.in_memory
                        prim_obj.in_memory = in_memory1

                        in_memory_date1= sec_obj.in_memory_date
                        sec_obj.in_memory_date = prim_obj.in_memory_date
                        prim_obj.in_memory_date= in_memory_date1

                        relation1= sec_obj.relation
                        sec_obj.relation = prim_obj.relation
                        prim_obj.relation= relation1

                        try:
                            temp_num = prim_obj.phone_no_primary
                            token_obj = Token.objects.get(user__username=temp_num)
                            token_obj.delete()
                        except:
                            temp_num = sec_obj.phone_no_secondary_user
                            token_obj = Token.objects.get(user__username=temp_num)
                            token_obj.delete()

                        sec_obj.save()
                        prim_obj.save()
            except:
                pass


        try:
            if member.usertype_from == 'PRIMARY':
                prim_obj = FileUpload.objects.get(primary_user_id = int(member.request_from))
                # sec_obj = Members.objects.get(secondary_user_id = int(member.request_to))
                user_details_str = "Your request for status change has been accepted"
                not_obj = Notification.objects.create(created_by_primary=prim_obj,
                          message=user_details_str)
                NoticeReadPrimary.objects.create(notification=not_obj, user_to=prim_obj)
            elif member.usertype_from == 'SECONDARY':
                # prim_obj = FileUpload.objects.get(primary_user_id = int(member.request_to))
                sec_obj = Members.objects.get(secondary_user_id = int(member.request_from))     
                user_details_str = "Your request for status change has been accepted"
                not_obj = Notification.objects.create(created_by_secondary=sec_obj,
                          message=user_details_str)
                NoticeReadPrimary.objects.create(notification=not_obj, user_to=sec_obj)
            else:
                pass
        except:
            pass
        member.status = 'Accepted'
        member.save()
        return Response({'success': True})

    @action(methods=['get'], detail=True, url_path='reject-primary',
        permission_classes=[IsAuthenticated, AdminPermission])
    def reject_primary(self, request, pk=None):
        member = self.get_object()
        try:
            if member.usertype_from == 'PRIMARY':
                prim_obj = FileUpload.objects.get(primary_user_id = int(member.request_from))
                # sec_obj = Members.objects.get(secondary_user_id = int(member.request_to))
                user_details_str = "Your request for status change has been rejected"
                not_obj = Notification.objects.create(created_by_primary=prim_obj,
                          message=user_details_str)
                NoticeReadPrimary.objects.create(notification=not_obj, user_to=prim_obj)
            elif member.usertype_from == 'SECONDARY':
                # prim_obj = FileUpload.objects.get(primary_user_id = int(member.request_to))
                sec_obj = Members.objects.get(secondary_user_id = int(member.request_from))     
                user_details_str = "Your request for status change has been rejected"
                not_obj = Notification.objects.create(created_by_secondary=sec_obj,
                          message=user_details_str)
                NoticeReadPrimary.objects.create(notification=not_obj, user_to=sec_obj)
            else:
                pass
        except:
            pass
        member.is_accepted = True
        member.status  = 'Rejected'
        member.save()
        return Response({'success': True})

#Phone number change

class PrimaryNumberChangeViewset(CreateAPIView):
    queryset = NumberChangePrimary.objects.all()
    serializer_class = NumberChangePrimarySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request_from_primary = request.POST.get('request_from_primary', False)
        number_from = request.POST.get('number_from', False)
        number_to = request.POST.get('number_to', False)

        if not request_from_primary and not number_from and not  number_to :
            return Response({'success': False,'message': 'You should fill all the fields'}, status=HTTP_400_BAD_REQUEST)
        else :
            # import pdb;pdb.set_trace()
            try:
                if FileUpload.objects.filter(primary_user_id=int(request_from_primary)).exists():
                    primary_user = FileUpload.objects.get(primary_user_id=request_from_primary)
                    if primary_user.phone_no_primary == number_from or primary_user.phone_no_secondary == number_from:
                        if NumberChangePrimary.objects.filter(request_from_primary=request_from_primary,number_to=number_to,number_from=number_from,status=None).exists():
                            data = {
                                'status': False,
                                'message':"You are already requested for number change"
                            }
                            data['response'] = {}

                            return Response(data, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            obj = NumberChangePrimary.objects.create(request_from_primary=request_from_primary,number_to=number_to,number_from=number_from)
                            try:
                                from_user = FileUpload.objects.get(phone_no_primary=request.user.username)
                            except:
                                from_user = FileUpload.objects.get(phone_no_secondary=request.user.username)

                            user_details={
                                "notification_id":obj.id,
                                "primary_user_id":from_user.primary_user_id,
                                "name":from_user.name,
                                "phone_number_primary":from_user.phone_no_primary,
                                "number_from": number_from,
                                "number_to": number_to,
                                "family_name":from_user.get_file_upload.first().name,
                                "prayer_group_name":from_user.get_file_upload_prayergroup.first().name,
                                "send_time":str(tz.now()),
                                "type":"number_change_primary",
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
                                image = ""
                                for admin_profile in admin_profiles:
                                    content = {'title':'Number Change Request','message':{"data":{"title":"Number Change Request","body":"%s,of %s,%s has requested to change his phone number."%(from_user.name,str(from_user.get_file_upload.first().name),str(from_user.get_file_upload_prayergroup.first().name)),"notificationType":"request","backgroundImage":image,"text_type":"long"},\
                                    "notification":{"alert":"This is a FCM notification","title":"Number Change Request","body":"%s,of %s,%s has requested to change his phone number"%(primary_user,str(primary_user.get_file_upload.first().name),str(primary_user.get_file_upload_prayergroup.first().name)),"sound":"default","backgroundImage":image,"backgroundImageTextColour":"#FFFFFF","image":image,"click_action":"request"}} } 
                                    
                                    content_ios = {'message':{"aps":{"alert":{"title":"Number Change Request","subtitle":"","body":"%s,of %s,%s has requested to change his phone number."%(from_user.name,str(from_user.get_file_upload.first().name),str(from_user.get_file_upload_prayergroup.first().name))},"sound":"default","category":"request","badge":1,"mutable-content":1},"media-url":image}}
                                    resp = fcm_messaging_to_user(admin_profile.user,content)
                                    resp1 = apns_messaging_to_user(admin_profile.user,content_ios)
                            except:
                                pass

                            success_data = {
                                'status': True,
                                "message": "Primary number change request is send successfully.Wait admin to approve/reject"
                            }
                            success_data['response'] = user_details
                            return Response(success_data, status=status.HTTP_201_CREATED)
                    else:

                        data = {
                            'status': False,
                            'message':"You have no permission to do this action"
                        }
                        data['response'] = {}

                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    data = {
                        'status': False,
                        'message':"Primary member doesnot exist"
                    }
                    data['response'] = {}

                    return Response(data, status=status.HTTP_400_BAD_REQUEST)

            except:
                return Response({'success': False,'message': 'Something Went Wrong'}, status=status.HTTP_400_BAD_REQUEST)


class PrimaryNumberChangeAcceptView(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    queryset = NumberChangePrimary.objects.all()
    serializer_class = NumberChangePrimarySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        data ={
            "success": True,
            "code": 200,
        }

        data['response'] = serializer.data

        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        data ={
            "success": True,
            "code": 200,
        }

        data['response'] = serializer.data

        return Response(data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        data ={
            "success": True,
            "code": 200,
        }

        data['response'] = serializer.data

        return Response(data)

    @action(methods=['get'], detail=True, url_path='approve-primary-number',
        permission_classes=[IsAuthenticated, AdminPermission])
    def approve_primary(self, request, pk=None):
        member = self.get_object()
        if member:
            try:

                prim_obj = FileUpload.objects.get(primary_user_id = int(member.request_from_primary))
                if prim_obj.phone_no_primary == member.number_from: 
                    temp_num = prim_obj.phone_no_primary  
                    prim_obj.phone_no_primary = member.number_to
                    try:
                        token_obj = Token.objects.get(user__username=temp_num)
                        token_obj.delete()
                    except:
                        pass
                    prim_obj.save()
                elif (prim_obj.phone_no_secondary == member.number_from):
                    temp_num = prim_obj.phone_no_secondary
                    prim_obj.phone_no_secondary = member.number_to
                    try:
                        token_obj = Token.objects.get(user__username=temp_num)
                        token_obj.delete()
                    except:
                        pass
                    prim_obj.save()
                else:
                    return Response({'success': False})
            except:
                pass
        try:
            user_details_str = "Your request for number change has been accepted"
            not_obj = Notification.objects.create(created_by_primary=prim_obj,
                      message=user_details_str)
            NoticeReadPrimary.objects.create(notification=not_obj, user_to=prim_obj)
        except:
            pass

        try:
            image = ""
            user=User.objects.get(username=prim_obj.phone_no_primary)
            content = {'title':'Number Changed','message':{"data":{"title":"Number Changed","body":"Your request for number change has been accepted","notificationType":"default","backgroundImage":image},\
            "notification":{"alert":"This is a FCM notification","title":"Number Changed","body":"Your request for number change has been accepted","sound":"default","backgroundImage":image,"backgroundImageTextColour":"#FFFFFF","image":image,"click_action":"default"}} } 

            content_ios = {'message':{"aps":{"alert":{"title":"Number Changed","subtitle":"","body":"Your request for number change has been accepted"},"sound":"default","category":"default","badge":1,"mutable-content":1},"media-url":image}}
            resp = fcm_messaging_to_user(user,content)
            resp1 = apns_messaging_to_user(user,content_ios)
        except:
            pass
        member.status = 'Accepted'
        member.save()
        # member.delete()
        return Response({'success': True})

    @action(methods=['get'], detail=True, url_path='reject-primary-number',
        permission_classes=[IsAuthenticated, AdminPermission])
    def reject_primary(self, request, pk=None):
        member = self.get_object()  
        try:
            prim_obj = FileUpload.objects.get(primary_user_id = int(member.request_from_primary))
            user_details_str = "Your request for number change has been rejected"
            not_obj = Notification.objects.create(created_by_primary=prim_obj,
                      message=user_details_str)
            NoticeReadPrimary.objects.create(notification=not_obj, user_to=prim_obj)
        except:
            pass

        try:
            image = ""
            user=User.objects.get(username=prim_obj.phone_no_primary)
            content = {'title':'Request Rejected','message':{"data":{"title":"Request Rejected","body":"Your request for number change has been rejected","notificationType":"default","backgroundImage":image},\
            "notification":{"alert":"This is a FCM notification","title":"Request Rejected","body":"Your request for number change has been rejected","sound":"default","backgroundImage":image,"backgroundImageTextColour":"#FFFFFF","image":image,"click_action":"default"}} } 
            
            content_ios = {'message':{"aps":{"alert":{"title":"Request Rejected","subtitle":"","body":"Your request for number change has been rejected"},"sound":"default","category":"default","badge":1,"mutable-content":1},"media-url":image}}
            resp = fcm_messaging_to_user(user,content)
            resp1 = apns_messaging_to_user(user,content_ios)
        except:
            pass
        member.is_accepted = True
        member.status  = 'Rejected'
        member.save()
        return Response({'success': True})


class AdminRequestSectionView(ModelViewSet):
    queryset = NumberChangePrimary.objects.all().order_by('date').reverse()
    serializer_class = AdminRequestSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):

        obj = PrimaryToSecondary.objects.all().order_by('date').reverse()
        serializerdata = PrimaryToSecondarySerializer(obj,many=True)

        obj_unapprove = UnapprovedMember.objects.all().order_by('date').reverse()
        serializerdata_unapprove = UnapprovedMemberSerializer(obj_unapprove,many=True)


        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset,many=True)
        data ={
            "success": True,
            "code": 200,
        }
        response =[]
        # response.append(serializer.data[0])
        # if serializerdata.data:
        #     response.append(serializerdata.data)
        for numlist in serializer.data:
            response.append(numlist)
        for statuslist in serializerdata.data:
            response.append(statuslist)
        for unapprovelists in serializerdata_unapprove.data:
            response.append(unapprovelists)
        response.sort(key=lambda item:item['date'], reverse=True)
        data['response'] = response
        return Response(data)

class UserDetailViewPage(APIView):
    queryset = FileUpload.objects.all()
    serializer_class = UserRetrieveSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request,*args,**kwargs):
        usertype_to = None
        usertype_from = None
        request_from = None
        request_to = None
        is_accepted = False
        member = None
        date_om = None
        
        user_type=request.GET['user_type']
        if not user_type:
            return Response({'success': False,'message':'Please provide user type'}, status=HTTP_400_BAD_REQUEST)

        try:
            member=FileUpload.objects.get(phone_no_primary=self.request.user.username)

            if member:
                request_from = member
                usertype_from = 'PRIMARY'
        except:
            member=Members.objects.filter(phone_no_secondary_user=self.request.user.username)

            if member:
                request_from = member
                usertype_from = 'SECONDARY'

        try:
            if user_type=='SECONDARY':
                user_details=Members.objects.get(secondary_user_id=self.kwargs['pk'])
                request_to = user_details
                usertype_to = 'SECONDARY'
                try:
                    phoneobj=ViewRequestNumber.objects.filter(request_from=member.pk,usertype_from=usertype_from,request_to=request_to.pk,usertype_to=usertype_to)
                    is_accepted = phoneobj.first().is_accepted
                except:
                    is_accepted = False
                try:
                    image=request.build_absolute_uri(user_details.image.url)
                except:
                    image='null'
                try :
                    if user_details.marrige_date :
                        date_om = user_details.marrige_date
                    elif user_details.dom:
                        date_om = user_details.dom
                    else:
                        pass
                except:
                    date_om = None

                try:
                    family_id = user_details.primary_user_id.get_file_upload.first().id
                except:
                    family_id = None
                try:
                    family_name = user_details.primary_user_id.get_file_upload.first().name
                except:
                    family_name = None

                
                data={
                    'name':user_details.member_name,
                    'address':user_details.primary_user_id.address,
                    'is_accepted':is_accepted,
                    'phone_no_primary':user_details.phone_no_secondary_user,
                    'phone_no_secondary':user_details.phone_no_secondary_user_secondary,
                    'dob':user_details.dob,
                    'dom':date_om,
                    'blood_group':user_details.blood_group,
                    'email':user_details.email,
                    'occupation':user_details.occupation,
                    'about':user_details.about,
                    'marital_status':user_details.marital_status,
                    'marrige_date':date_om,
                    'in_memory':user_details.in_memory,
                    'in_memory_date':user_details.in_memory_date,
                    'image':image,
                    'relation':user_details.relation,
                    'family_id':family_id,
                    'family_name':family_name,
                    'primary_user':user_details.primary_user_id.name,
                    'primary_user_id':user_details.primary_user_id.primary_user_id,
                    'primary_in_memory':user_details.primary_user_id.in_memory,
                    'primary_user_name':user_details.primary_user_id.name

                }
                return Response({'success': True,'message':'Profile found successfully','user_details':data}, status=HTTP_200_OK)
            else:
                try:
                    user_details=FileUpload.objects.get(primary_user_id=self.kwargs['pk'])

                    request_to = user_details
                    usertype_to = 'PRIMARY'
                    try:
                        phoneobj=ViewRequestNumber.objects.filter(request_from=member.pk, usertype_from=usertype_from,\
                            request_to=request_to.pk, usertype_to=usertype_to)
                        is_accepted = phoneobj.first().is_accepted
                    except:
                        is_accepted = False
                    try:
                        image=request.build_absolute_uri(user_details.image.url)
                    except:
                        image='null'
                    try :
                        if user_details.marrige_date :
                            date_om = user_details.marrige_date
                        elif user_details.dom:
                            date_om = user_details.dom
                        else:
                            pass
                    except:
                        date_om = None

                    try:
                        family_id = user_details.get_file_upload.first().id
                    except:
                        family_id = None

                    try:
                        family_name = user_details.get_file_upload.first().name
                    except:
                        family_name = None

                    data={
                       'name':user_details.name,
                       'address':user_details.address,
                       'is_accepted':is_accepted,
                       'phone_no_primary':user_details.phone_no_primary,
                       'phone_no_secondary':user_details.phone_no_secondary,
                       'dob':user_details.dob,
                       'dom':date_om,
                       'blood_group':user_details.blood_group,
                       'email':user_details.email,
                       'occupation':user_details.occupation,
                       'about':user_details.about,
                       'marital_status':user_details.marital_status,
                       'marrige_date':date_om,
                       'in_memory':user_details.in_memory,
                       'in_memory_date':user_details.in_memory_date,
                       'image':image,
                       'relation':user_details.relation,
                       'family_id':family_id,
                       'family_name':family_name,
                       'primary_user':user_details.name,
                       'primary_user_id':user_details.primary_user_id,
                       'primary_in_memory':user_details.in_memory,
                       'primary_user_name':user_details.name
                    }
                    return Response({'success': True,'message':'Profile found successfully','user_details':data}, status=HTTP_200_OK)
                except:
                    user_details=AdminProfile.objects.get(id=self.kwargs['pk'])
                    data={
                        'id':user_details.user,
                        'mobile_number':user_details.mobile_number
                    }
                    return Response({'success': True,'message':'Profile found successfully','user_details':data}, status=HTTP_200_OK)
        except:
            return Response({'success': False,'message':'Something Went Wrong'}, status=HTTP_400_BAD_REQUEST)


class UserDownloadView(ModelViewSet):
    queryset = FileUpload.objects.all()
    # serializer_class = UserRetrieveSerializer
    # permission_classes = [IsAdminUser]
    # authentication_classes = [TokenAuthentication]

    def list(self, request, *args, **kwargs):
        # import pdb;pdb.set_trace()
        if request.GET.get('csv') == 'True':
            if request.GET.get('prayer_group'):
                paraye_group_name = request.GET.get('prayer_group')
                prayer_obj = PrayerGroup.objects.get(name__iexact=paraye_group_name)
                primary_qs = FileUpload.objects.all()
                if primary_qs:
                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = ('attachment; filename="%s.csv"') % (prayer_obj.name)
                    writer = csv.writer(response)
                    writer.writerow(['SL NO','PRAYER GROUP','NAME','FAMILY NAME','FAMILY ABOUT','FAMILY IMAGE',\
                                    'MEMBERS','RELATION','PHONE NO PRIMARY','PHONE NO SECONDARY','EMAIL','ADDRESS','USER IMAGE',\
                                    'OCCUPATION','OCCUPATION DESCRIPTION','ABOUT USER','DOB','DOM','BLOOD GROUP','MEMORY DATE (YYYY-MM-DD)','ID_PRIMARY','ID_SECONDARY'
                                    ])
                    count = 1
                    for user in primary_qs:
                        if user.get_file_upload_prayergroup.first().name == prayer_obj.name: 
                            output1 = []
                            output2 = []
                            try:
                                user_id = user.primary_user_id
                                prayer_obj = PrayerGroup.objects.get(primary_user_id=user_id)
                                family_obj = Family.objects.get(primary_user_id=user_id)
                                if user.image :
                                    img=user.image.url
                                else:
                                    img = ''
                                if family_obj.image :
                                    img_fam=family_obj.image.url
                                else:
                                    img_fam = ''
                                try :
                                    if user.marrige_date :
                                        dom = user.marrige_date
                                    elif user.dom:
                                        dom = user.dom
                                    else:
                                        pass
                                except:
                                    dom = ''
                                try :
                                    if user.in_memory_date:
                                        in_memory = str(user.in_memory_date.date())
                                    else:
                                        in_memory = ''
                                except:
                                    in_memory = ''
                                occupation_description = ''
                                occupation = ''
                                if user.occupation:
                                        if user.occupation.split('---') :
                                            occupation = str(user.occupation.split('---')[0])
                                        else:
                                            occupation = ''
                                        try:
                                            if user.occupation.split('---') : 
                                                occupation_description = user.occupation.split('---')[1]
                                            else:
                                                occupation_description = ''
                                        except:
                                            pass
                                else:
                                    occupation = ''
                                    occupation_description = ''

                                writer.writerows([''])
                                output1.append([count,prayer_obj.name,user.name,family_obj.name,family_obj.about,img_fam,\
                                    '',user.relation,user.phone_no_primary,user.phone_no_secondary,user.email,user.address,img,\
                                    occupation,occupation_description,user.about,user.dob,dom,user.blood_group,in_memory,user.primary_user_id,''])
                                writer.writerows(output1)
                                count = count + 1
                                try:
                                    
                                    mem_obj=Members.objects.filter(primary_user_id=user_id)
                                    for mem in mem_obj:
                                        if mem.image :
                                            img_mem=mem.image.url
                                        else:
                                            img_mem = ''
                                        dom_sec = ''
                                        try :
                                            if mem.marrige_date :
                                                dom_sec = mem.marrige_date
                                            elif mem.dom:
                                                dom_sec = mem.dom
                                            else:
                                                pass
                                        except:
                                            dom_sec = ''
                                        try :
                                            in_memory = str(mem.in_memory_date.date())
                                        except:
                                            in_memory = ''

                                        occupation_description_sec = ''
                                        occupation_sec = ''
                                        if mem.occupation:
                                                if mem.occupation.split('---') :
                                                    occupation_sec = str(mem.occupation.split('---')[0])
                                                else:
                                                    occupation_sec = ''
                                                try:
                                                    if mem.occupation.split('---') : 
                                                        occupation_description_sec = mem.occupation.split('---')[1]
                                                    else:
                                                        occupation_description_sec = ''
                                                except:
                                                    pass
                                        else:
                                            occupation_sec = ''
                                            occupation_description_sec = ''
                                        output2.append(['','','','','','',mem.member_name,mem.relation,mem.phone_no_secondary_user,mem.phone_no_secondary_user_secondary,mem.email,'',\
                                            img_mem,occupation_sec,occupation_description_sec,mem.about,mem.dob,dom_sec,mem.blood_group,in_memory,'',mem.secondary_user_id])
                                    writer.writerows(output2)
                                except:
                                    pass

                            except:
                                pass
                    return response

            else:
                primary_qs = FileUpload.objects.all()
                if primary_qs:
                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename="users_list.csv"'
                    writer = csv.writer(response)
                    writer.writerow(['SL NO','PRAYER GROUP','NAME','FAMILY NAME','FAMILY ABOUT','FAMILY IMAGE',\
                                    'MEMBERS','RELATION','PHONE NO PRIMARY','PHONE NO SECONDARY','EMAIL','ADDRESS','USER IMAGE',\
                                    'OCCUPATION','OCCUPATION DESCRIPTION','ABOUT USER','DOB','DOM','BLOOD GROUP','MEMORY DATE (YYYY-MM-DD)','ID_PRIMARY','ID_SECONDARY'
                                    # ,'Martial_Status','Memory_Date'
                                    ])
                    count = 1
                    for user in primary_qs:
                        output1 = []
                        output2 = []
                        try:
                            user_id = user.primary_user_id
                            prayer_obj = PrayerGroup.objects.get(primary_user_id=user_id)
                            family_obj = Family.objects.get(primary_user_id=user_id)
                            if user.image :
                                img=user.image.url
                            else:
                                img = ''
                            if family_obj.image :
                                img_fam=family_obj.image.url
                            else:
                                img_fam = ''

                            dom = ''
                            try :
                                if user.marrige_date :
                                    dom = user.marrige_date
                                elif user.dom:
                                    dom = user.dom
                                else:
                                    pass
                            except:
                                dom = ''
                            try :
                                in_memory = str(user.in_memory_date.date())
                            except:
                                in_memory = ''

                            occupation_description = ''
                            occupation = ''
                            if user.occupation:
                                    if user.occupation.split('---') :
                                        occupation = str(user.occupation.split('---')[0])
                                    else:
                                        occupation = ''
                                    try:
                                        if user.occupation.split('---') : 
                                            occupation_description = user.occupation.split('---')[1]
                                        else:
                                            occupation_description = ''
                                    except:
                                        pass
                            else:
                                occupation = ''
                                occupation_description = ''
                            writer.writerows([''])
                            output1.append([count,prayer_obj.name,user.name,family_obj.name,family_obj.about,img_fam,\
                                '',user.relation,user.phone_no_primary,user.phone_no_secondary,user.email,user.address,img,\
                                occupation,occupation_description,user.about,user.dob,dom,user.blood_group,in_memory,user.primary_user_id,''])
                            writer.writerows(output1)
                            count = count + 1
                            try:
                                mem_obj=Members.objects.filter(primary_user_id=user_id)
                                for mem in mem_obj:
                                    if mem.image :
                                        img_mem=mem.image.url
                                    else:
                                        img_mem = ''
                                    dom_sec = ''
                                    try :
                                        if mem.marrige_date :
                                            dom_sec = mem.marrige_date
                                        elif mem.dom:
                                            dom_sec = mem.dom
                                        else:
                                            pass
                                    except:
                                        dom_sec = ''
                                    try :
                                        in_memory = str(mem.in_memory_date.date())
                                    except:
                                        in_memory = ''

                                    occupation_description_sec = ''
                                    occupation_sec = ''
                                    if mem.occupation:
                                            if mem.occupation.split('---') :
                                                occupation_sec = str(mem.occupation.split('---')[0])
                                            else:
                                                occupation_sec = ''
                                            try:
                                                if mem.occupation.split('---') : 
                                                    occupation_description_sec = mem.occupation.split('---')[1]
                                                else:
                                                    occupation_description_sec = ''
                                            except:
                                                pass
                                    else:
                                        occupation_sec = ''
                                        occupation_description_sec = ''

                                    output2.append(['','','','','','',mem.member_name,mem.relation,mem.phone_no_secondary_user,mem.phone_no_secondary_user_secondary,mem.email,'',\
                                        img_mem,occupation_sec,occupation_description_sec,mem.about,mem.dob,dom_sec,mem.blood_group,in_memory,'',mem.secondary_user_id])
                                writer.writerows(output2)
                            except:
                                pass

                        except:
                            pass
                    return response
        return Response({'success': True,'message':'User Details downloaded successfully'}, status=HTTP_200_OK)

class CreateMemoryUserView(APIView):
    serializer_class = UserMemorySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        serializer = UserMemorySerializer(data=request.data,context={'request':request})

        if serializer.is_valid():

            family = Family.objects.get(pk=serializer.data['family'])
            
            if family.primary_user_id and not family.primary_user_id.in_memory and serializer.data['member_type'] in ['Primary', 'primary']:
                data = {
                    'status': False,
                    'message': 'Primary user already exists for this family'
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            if serializer.data['member_type'] in ['Primary', 'primary']:
                
                instance = FileUpload(
                    name=serializer.data['name'],
                    dob=serializer.data['dob'],
                    in_memory_date=serializer.data['in_memory_date'],

                )
            else:
                if not family.primary_user_id:
                    data = {
                        'status': False,
                        'message': 'Create a primary user to add secondary users'
                    }
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)

                instance = Members(
                    member_name=serializer.data['name'],
                    dob=serializer.data['dob'],
                    in_memory_date=serializer.data['in_memory_date']
                )

            if serializer.data['member_status'] == 'in_memory':
                instance.in_memory = True

            if request.FILES.get('image'):
                instance.image = request.FILES['image']

            instance.save()

            if serializer.data['family']:

                if serializer.data['member_type'] in ['Primary', 'primary']:
                    family.primary_user_id = instance

                else:
                    instance.primary_user_id  = family.primary_user_id
                    instance.save()

                family.save()


            if serializer.data['prayer_group']:
                prayer_group = PrayerGroup.objects.get(pk=serializer.data['prayer_group'])
                
                if serializer.data['member_type'] in ['Primary', 'primary']:
                    prayer_group.primary_user_id.add(instance)
                else:
                    prayer_group.primary_user_id.add(instance.primary_user_id)
                
                data ={
                    'id': instance.pk
                }
                data.update(serializer.data)

                response={
                    "status": True,
                    "message": "User Created successfully"
                }

                response['response'] = data

            return Response(response)

        data={
            'status': False,
        }
        data['response'] = serializer.errors

        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class CreateFamilyMemoryUserView(CreateAPIView):
    # queryset = NoticeBereavement.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prayer_group_id = request.POST.get('prayer_group', False)
        family_id = request.POST.get('family', False)
        member_id=request.POST.get('member_id', False)
        user_type=request.POST.get('member_type', False)
        member_status=request.POST.get('member_status', False)
        in_memory_date = request.POST.get('in_memory_date', False)
        dob = request.POST.get('dob', '')
        # title=request.POST.get('title', False)
        # import pdb;pdb.set_trace()
        if not prayer_group_id and not family_id and not member_id and not user_type and not member_status and not in_memory_date and not dob:
            return Response({'success': False,'message': 'You should fill all the fields'}, status=HTTP_400_BAD_REQUEST)
        else:
            if not prayer_group_id:
                return Response({'success': False,'message': 'Prayer group field shouldnot be blank'}, status=HTTP_400_BAD_REQUEST)
            if not family_id:
                return Response({'success': False,'message': 'Family field shouldnot be blank'}, status=HTTP_400_BAD_REQUEST)
            if not member_id:
                return Response({'success': False,'message': 'Member field shouldnot be blank'}, status=HTTP_400_BAD_REQUEST)
            if not in_memory_date:
                return Response({'success': False,'message': 'In_memory_date field shouldnot be blank'}, status=HTTP_400_BAD_REQUEST)
            if not user_type:
                return Response({'success': False,'message': 'Member type field shouldnot be blank'}, status=HTTP_400_BAD_REQUEST)
            if not member_status:
                return Response({'success': False,'message': 'Member status field shouldnot be blank'}, status=HTTP_400_BAD_REQUEST)
            if prayer_group_id and member_id and family_id and in_memory_date and user_type and member_status:
                try:
                    prayer_group_id=PrayerGroup.objects.get(id=prayer_group_id)
                except:
                    return Response({'success': False,'message': 'Prayer Group doesnot exist'}, status=HTTP_400_BAD_REQUEST)
                try:
                    family_id=Family.objects.get(id=family_id)
                except:
                    return Response({'success': False,'message': 'Family doesnot exist'}, status=HTTP_400_BAD_REQUEST)

                if user_type=='SECONDARY' or user_type=='secondary':
                    try:
                        member_id=Members.objects.get(secondary_user_id=member_id)
                    except:
                        return Response({'success': False,'message': 'Member doesnot exist'}, status=HTTP_400_BAD_REQUEST)
                    # beri_obj=NoticeBereavement.objects.create(prayer_group=prayer_group_id,family=family_id,secondary_member=member_id,description=description)
                    if member_status == 'in_memory':
                        member_id.in_memory = True
                        member_id.in_memory_date=datetime.strptime(in_memory_date, "%Y-%m-%d %H:%M:%S")
                        member_id.dob = dob
                        try:
                            if request.FILES.get('image'):
                                member_id.image = request.FILES['image']
                            else:
                                pass
                        except:
                            pass
                        member_id.save()

                    return Response({'success': True,'message':'User Updated Successfully'}, status=HTTP_201_CREATED)
                elif user_type=='PRIMARY' or user_type=='primary':
                    try:
                        member_id=FileUpload.objects.get(primary_user_id=member_id)
                    except:
                        return Response({'success': False,'message': 'Member doesnot exist'}, status=HTTP_400_BAD_REQUEST)
                    # beri_obj = NoticeBereavement.objects.create(prayer_group=prayer_group_id,family=family_id,primary_member=member_id,description=description)
                    if member_status == 'in_memory':
                        member_id.in_memory=True
                        member_id.in_memory_date=datetime.strptime(in_memory_date, "%Y-%m-%d %H:%M:%S")
                        member_id.dob = dob
                        try:
                            if request.FILES.get('image'):
                                member_id.image = request.FILES['image']
                            else:
                                pass
                        except:
                            pass
                        member_id.save()
                    return Response({'success': True,'message':'User Updated Successfully'}, status=HTTP_201_CREATED)
                else:
                    return Response({'success': False,'message': 'Invalid User'}, status=HTTP_400_BAD_REQUEST)


class UpdateUserByMembersView(APIView):
    serializer_class = UserByMembersSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
   
    def post(self, request, pk=None, format=None):
        response_data = []
        serializer = UserByMembersSerializer(data=request.data)

        if serializer.is_valid():

            prayer_group = PrayerGroup.objects.get(pk=serializer.data['prayer_group'])
            family = Family.objects.get(pk=serializer.data['family'])

            if serializer.data['member_type'] in ['Primary', 'primary','PRIMARY']:
                instance = FileUpload.objects.get(pk=pk)

                instance.name = serializer.data['name']
                instance.dob = serializer.data['dob']
                instance.blood_group = serializer.data['blood_group']
                instance.email = serializer.data['email']
                # instance.phone_no_primary = serializer.data['primary_number']
                instance.phone_no_secondary = serializer.data['secondary_number']
                instance.occupation = serializer.data['occupation']
                instance.marital_status = serializer.data['marital_status']
                instance.marrige_date = serializer.data['marrige_date']
                instance.about = serializer.data['about']
                instance.landline= serializer.data['landline']
                instance.relation= serializer.data['relation']
                instance.in_memory_date= serializer.data['in_memory_date']
                instance.save()

                previous_groups = instance.get_file_upload_prayergroup.all()
                
                for group in previous_groups:
                    group.primary_user_id.remove(instance)
                
                prayer_group.primary_user_id.add(instance)

                for pre_family in instance.get_file_upload.all():
                    pre_family.primary_EachUserNotificationuser_id = None
                    pre_family.save()

                family.primary_user_id = instance
                family.save()

            else:
                if serializer.data['member_type'] in ['Secondary', 'secondary','SECONDARY']:
                    if not family.primary_user_id in prayer_group.primary_user_id.all():
                        data = {
                            'status': False,
                            'message': 'Invalid prayer group for family'
                        }
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)

                    instance = Members.objects.get(pk=pk)
                    instance.member_name = serializer.data['name']
                    instance.dob = serializer.data['dob']
                    instance.blood_group = serializer.data['blood_group']
                    instance.email = serializer.data['email']
                    instance.phone_no_secondary_user = serializer.data['primary_number']
                    instance.phone_no_secondary_user_secondary = serializer.data['secondary_number']
                    instance.occupation = serializer.data['occupation']
                    instance.marital_status = serializer.data['marital_status']
                    instance.marrige_date = serializer.data['marrige_date']
                    instance.about = serializer.data['about']
                    instance.landline= serializer.data['landline']
                    instance.relation= serializer.data['relation']
                    instance.in_memory_date= serializer.data['in_memory_date']
                    instance.save()

                    instance.primary_user_id = family.primary_user_id

                    if instance.primary_user_id:
                        previous_groups = instance.primary_user_id.get_file_upload_prayergroup.all()
                        
                        for group in previous_groups:
                            group.primary_user_id.remove(instance.primary_user_id)

                        prayer_group = PrayerGroup.objects.get(pk=serializer.data['prayer_group'])
                        prayer_group.primary_user_id.add(instance.primary_user_id)


                    instance.save()
                else:
                    data={
                        'status': False,
                        'message':"Invalid Member Type"
                    }
                    data['response'] = {}

                    return Response(data, status=status.HTTP_400_BAD_REQUEST) 

            if serializer.data['member_status'] == 'in_memory':
                instance.in_memory = True

            if serializer.data['member_status'] == 'active':
                instance.in_memory = False

            if request.FILES.get('image'):
                instance.image = request.FILES['image']

            instance.save()

            data ={
                'id': instance.pk
            }
            data.update(serializer.data)
            response_data.append(data)

            response={
                "status": True,
                "message": "User Updated by User Successfully",
                "response":response_data
            }

            # response['response'] = data

            return Response(response)

        data={
            'status': False,
        }
        data['response'] = serializer.errors

        return Response(data, status=status.HTTP_400_BAD_REQUEST)

class DeviceInactiveView(APIView):
    # queryset = FileUpload.objects.all()
    # serializer_class = UserRetrieveSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request,*args,**kwargs):
        registration_id = request.GET['registration_id']
        cloud_message_type = request.GET['cloud_message_type']
        if not registration_id and not cloud_message_type:
            return Response({'success': False,'message':'Please provide registration_id and cloud_message_type'}, status=HTTP_400_BAD_REQUEST)
        try:
            if cloud_message_type == 'FCM' or cloud_message_type == 'fcm' :

                gcm_device = GCMDevice.objects.get(registration_id=registration_id,active=True)
                gcm_device.delete()
                return Response({'success': True,'message':'Device deactiveted successfully'}, status=HTTP_200_OK)

            elif cloud_message_type == 'APNS' or cloud_message_type == 'apns' :
                apns_device = APNSDevice.objects.get(registration_id=registration_id,active=True)
                apns_device.delete()
                return Response({'success': True,'message':'Device deactiveted successfully'}, status=HTTP_200_OK)
            else:
                return Response({'success': False,'message':'No device found'}, status=HTTP_400_BAD_REQUEST)
        except:
            return Response({'success': False,'message':'Invalid Details'}, status=HTTP_400_BAD_REQUEST)