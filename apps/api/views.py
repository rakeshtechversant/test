from django.shortcuts import render
from django.contrib.auth import password_validation, authenticate
from django.db.models import Q
from django.http import Http404
# Create your views here.

from rest_framework import mixins
from rest_framework import exceptions
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
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

from apps.api.permissions import IsOwnerOrReadOnly
from apps.api.utils import MultipartJsonParser
from apps.api.serializers import ChurchHistorySerializer,ChurchImagesSerializer,LoginSerializer, FamilyListSerializer, UserRegistrationMobileSerializer, \
    PrayerGroupAddMembersSerializer, PrayerGroupAddSerializer, UserListSerializer, UserRetrieveSerializer, \
    UserCreateSerializer, ChurchVicarSerializer, FileUploadSerializer, OTPVeifySerializer, SecondaryaddSerializer, \
    MembersSerializer, NoticeSerializer
from apps.church.models import  Members, Family, UserProfile, ChurchDetails, FileUpload, OtpModels, \
    PrayerGroup, Notification, Notice
from apps.api.models import AdminProfile
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, \
HTTP_404_NOT_FOUND
from django.utils.crypto import get_random_string
from twilio.rest import Client
from church_project import settings
from datetime import datetime, timezone


class UserLoginMobileView(APIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserRegistrationMobileSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        mobile_number = request.data['mobile_number']
        if not mobile_number:
            return Response({'message': 'Mobile field should not be blank', 'success': False},
                            status=HTTP_400_BAD_REQUEST)
        else:
            if AdminProfile.objects.filter(mobile_number=mobile_number):
                admin_profile = AdminProfile.objects.get(mobile_number=mobile_number)
                if mobile_number == admin_profile.mobile_number:
                    user=User.objects.get(username=admin_profile.user)
                    token, created = Token.objects.get_or_create(user=user)
                    data = {
                        'mobile': admin_profile.mobile_number,
                        'user_type': 'ADMIN',
                        'name': 'admin',
                        'token':token.key
                    }
                    otp_number = get_random_string(length=6, allowed_chars='1234567890')

                    try:
                        OtpModels.objects.filter(mobile_number=mobile_number).delete()
                    except:
                        pass

                    OtpModels.objects.create(mobile_number=mobile_number, otp=otp_number)
                    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

                    message = client.messages.create(to='+91' + mobile_number, from_='+15036837180', body=otp_number)
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
                                'token':token.key
                            }
                            otp_number = get_random_string(length=6, allowed_chars='1234567890')
                            try:
                                OtpModels.objects.filter(mobile_number=mobile_number).delete()
                            except:
                                pass
                            OtpModels.objects.create(mobile_number=mobile_number, otp=otp_number)
                            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                            message = client.messages.create(to='+91' + mobile_number, from_='+15036837180',
                                                             body=otp_number)
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
                                'token':token.key
                            }
                            otp_number = get_random_string(length=6, allowed_chars='1234567890')
                            try:
                                OtpModels.objects.filter(mobile_number=user_profile.phone_no_primary).delete()
                            except:
                                pass
                            OtpModels.objects.create(mobile_number=user_profile.phone_no_primary, otp=otp_number)
                            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                            message = client.messages.create(to='+91' + user_profile.phone_no_primary, from_='+15036837180',
                                                             body=otp_number)
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
                                'phone_no_primary' : user_profile.primary_user_id.phone_no_primary
                            }

                            otp_number = get_random_string(length=6, allowed_chars='1234567890')

                            try:
                                OtpModels.objects.filter(mobile_number=user_profile.phone_no_secondary_user).delete()
                            except:
                                pass

                            OtpModels.objects.create(mobile_number=user_profile.phone_no_secondary_user, otp=otp_number)
                            
                            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

                            message_body = user_profile.member_name + ' requested OTP for login: ' + otp_number

                            message = client.messages.create(to='+91' + user_profile.primary_user_id.phone_no_primary,
                                                             from_='+15036837180', body=message_body)

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
                                        'success': False, 'user_mobile': data}, status=HTTP_400_BAD_REQUEST)


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
            otp_obj.is_expired = True
            otp_obj.save()
            
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
                            'primary_name':member.primary_user_id.name
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

class UserListView(ListAPIView):
    queryset = FileUpload.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [AllowAny]


class FamilyListView(ListAPIView):
    queryset = Family.objects.all()
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


class UserDeleteView(DestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]


class UserDetailView(RetrieveAPIView):
    queryset = FileUpload.objects.all()
    serializer_class = UserRetrieveSerializer
    permission_classes = [IsAuthenticated]
    # lookup_field = 'user'
    # lookup_url_kwarg = "abc"


class ChurchVicarView(RetrieveAPIView):
    queryset = ChurchDetails.objects.all()
    serializer_class = ChurchVicarSerializer
    permission_classes = [IsAdminUser]


class ChurchHistoryView(RetrieveAPIView):
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


class PrayerGroupMemberaddView(CreateAPIView):
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
    queryset = PrayerGroup.objects.all()
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
    queryset = PrayerGroup.objects.all()
    serializer_class = PrayerGroupAddSerializer
    permission_classes = [AllowAny]

    def get_queryset(self, *args, **kwargs):
        prayer_id = self.kwargs['pk']
        
        try:
            prayer_group = PrayerGroup.objects.get(id=prayer_id)
        except PrayerGroup.DoesNotExist:
            raise exceptions.NotFound(detail="Prayer group does not exist")
        
        family_list = Family.objects.filter(primary_user_id=prayer_group.primary_user_id)
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

            return Response(data)


        serializer = self.get_serializer(queryset, many=True)

        data = {
            'code': 200,
            'status': "OK",
            'response': serializer.data
        }

        return Response(data)




class NoticeModelViewSet(ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = [IsAdminUser]

class SendOtp(APIView):

    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        
        try:
            user = Members.objects.get(secondary_user_id=user_id)
        except Members.DoesNotExist:
            raise exceptions.NotFound(detail="User does not exist")
        
        superusers = User.objects.filter(is_superuser=True).first()
        
        # if user.primary_user_id:
        #     return Response({'success': False,'message': superusers.}, status=HTTP_400_BAD_REQUEST)

