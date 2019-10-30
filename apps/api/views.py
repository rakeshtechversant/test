from django.shortcuts import render
from django.contrib.auth import password_validation, authenticate
# Create your views here.
from rest_framework import mixins
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView,ListAPIView,RetrieveAPIView,RetrieveUpdateAPIView,DestroyAPIView,CreateAPIView,UpdateAPIView
from rest_framework import status
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from rest_framework import parsers
from rest_framework import viewsets

from apps.api.permissions import IsOwnerOrReadOnly
from apps.api.utils import MultipartJsonParser
from apps.api.serializers import LoginSerializer,FamilyListSerializer,UserRegistrationMobileSerializer,PrayerGroupAddMembersSerializer,PrayerGroupAddSerializer,UserListSerializer,UserRetrieveSerializer,UserCreateSerializer,ChurchAddUpdateSerializer,FileUploadSerializer,OTPVeifySerializer,SecondaryaddSerializer
from apps.church.models import Family,UserProfile,ChurchDetails,FileUpload,OtpModels,PrayerGroup, Notification
from rest_framework.status import HTTP_200_OK,HTTP_201_CREATED, HTTP_400_BAD_REQUEST , HTTP_401_UNAUTHORIZED
from django.utils.crypto import get_random_string
from twilio.rest import Client
from church_project import settings
from datetime import datetime, timezone

class UserCreateView(CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserCreateSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile_number = self.request.GET.get('mobile_number')
        user_type = self.request.GET.get('user_type')

        user_name = serializer.validated_data.get("user_name", None)
        password = serializer.validated_data.get("password", None)
        confirm_password = serializer.validated_data.get("confirm_password", None)

        if User.objects.filter(username=user_name).exists():
            return Response({'message': 'Username already exists','success':False},status=HTTP_400_BAD_REQUEST)
        if mobile_number and user_type:
            if user_type == 'PRIMARY':
                if(password ==  confirm_password):
                    user = User.objects.create(
                        username=user_name,
                    )
                    user.set_password(password)
                    user.save()
                    userprofile=UserProfile.objects.create(user=user,mobile_number = mobile_number,is_primary=True)
                    Notification.objects.create(user=userprofile,is_new_register=True,created_time=datetime.strptime('2018-02-16 11:00 AM', "%Y-%m-%d %I:%M %p"))
                    return Response({'success': True,'message':'User Profile Created Successfully'}, status=HTTP_201_CREATED)
                else:
                    return Response({'message': 'Password Missmatch','success':False},status=HTTP_400_BAD_REQUEST)
            elif user_type =='SECONDARY':
                if(password ==  confirm_password):
                    user = User.objects.create(
                        username=user_name,
                    )
                    user.set_password(password)
                    user.save()
                    userprofile=UserProfile.objects.create(user=user,mobile_number = mobile_number)
                    Notification.objects.create(user=userprofile,is_new_register=True,created_time=datetime.strptime('2018-02-16 11:00 AM', "%Y-%m-%d %I:%M %p"))
                    return Response({'success': True,'message':'User Profile Created Successfully'}, status=HTTP_201_CREATED)
                else:
                    return Response({'message': 'Password Missmatch','success':False},status=HTTP_400_BAD_REQUEST)
            elif user_type =='CHURCH':
                if(password ==  confirm_password):
                    user = User.objects.create(
                        username=user_name,
                    )
                    user.set_password(password)
                    user.save()
                    userprofile=UserProfile.objects.create(user=user,mobile_number = mobile_number,is_church_user=True)
                    Notification.objects.create(user=userprofile,is_new_register=True,created_time=datetime.strptime('2018-02-16 11:00 AM', "%Y-%m-%d %I:%M %p"))
                    return Response({'success': True,'message':'User Profile Created Successfully'}, status=HTTP_201_CREATED)
                else:
                    return Response({'message': 'Password Missmatch','success':False},status=HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Something Went Wrong','success':False},status=HTTP_400_BAD_REQUEST)
        else:   
            return Response({'message': 'Something Went Wrong','success':False},status=HTTP_400_BAD_REQUEST)

class UserRegistrationMobileView(CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserRegistrationMobileSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_count=0
        mobile_number = serializer.validated_data.get("mobile_number", None)
        user_type = serializer.validated_data.get("user_type", None)
        try:
            if user_type == 'PRIMARY' or user_type == 'SECONDARY' or user_type == 'CHURCH':
                if UserProfile.objects.filter(mobile_number = mobile_number).exists():
                    # raise serializers.ValidationError("This number is already taken")
                    return Response({'message': 'This number is already taken','success':False},status=HTTP_400_BAD_REQUEST)
                else:
                   if FileUpload.objects.filter(mobile_number=mobile_number):
                       user_count=user_count+1
                       if mobile_number:
                            otp_number = get_random_string(length=6, allowed_chars='1234567890')
                            try:
                                OtpModels.objects.filter(mobile_number=mobile_number).delete()
                            except:
                                pass
                            OtpModels.objects.create(mobile_number=mobile_number, otp=otp_number)
                            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                            message = client.messages.create(to='+91' + mobile_number, from_='+15036837180',body=otp_number)
                            return Response({'success': True,'message':'OTP Sent Successfully'}, status=HTTP_201_CREATED)
                   else:
                        if user_count == 0:
                            return Response({'message': 'We couldnt find your profile in database,Please contact service providers','success':False},status=HTTP_400_BAD_REQUEST)
                        else:
                            return Response({'message': 'Invalid usertype,Please select again','success':False},status=HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Invalid usertype,Please select again','success':False},status=HTTP_400_BAD_REQUEST)
        except:
        # raise serializers.ValidationError("Invalid usertype,Please select again")
            return Response({'message': 'Something Went Wrong','success':False},status=HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    queryset = User.objects.all()
    serializer_class = LoginSerializer


    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        username =  self.request.POST.get('username')
        password = self.request.POST.get('password')
        if not username:
            return Response({'message': 'This field should not be blank','success':False},status=HTTP_400_BAD_REQUEST)
        if not password:
            return Response({'message': 'This field should not be blank','success':False},status=HTTP_400_BAD_REQUEST)
        if username and password:
            user = authenticate(username=username, password=password)
            try:
                token, created = Token.objects.get_or_create(user=user)
                if user:
                    try:
                        userprofiles = UserProfile.objects.get(user=user)
                        if userprofiles.is_primary ==True:
                            data = {
                            'username': user.username,
                            'token': token.key,
                            'user_type': "PRIMARY"
                            }
                            return Response({'success': True,'message':'Login Successfully','user-details':data}, status=HTTP_200_OK)
                        elif userprofiles.is_church_user ==True:
                            data = {
                            'username': user.username,
                            'token': token.key,
                            'user_type': "CHURCH"
                            }
                            return Response({'success': True,'message':'Login Successfully','user-details':data}, status=HTTP_200_OK)
                        elif userprofiles.is_church_user ==False and userprofiles.is_primary==False:
                            data = {
                            'username': user.username,
                            'token': token.key,
                            'user_type': "SECONDARY"
                            }
                            return Response({'success': True,'message':'Login Successfully','user-details':data}, status=HTTP_200_OK)
                        else:
                            data = {
                            'username': user.username,
                            'token': token.key,
                            'user_type': "NO DATA"
                            }
                            return Response({'message': 'Something went wrong','success':False},status=HTTP_400_BAD_REQUEST)
                    except:
                        return Response({'message': 'Admin credentials,check with other users','success':False},status=HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message': 'Invalid credentials','success':False},status=HTTP_400_BAD_REQUEST)
            except:
                return Response({'message': 'Invalid credentials','success':False},status=HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class UserListView(ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserListSerializer
    permission_classes=[AllowAny]

class FamilyListView(ListAPIView):
    queryset = Family.objects.all()
    serializer_class = FamilyListSerializer
    permission_classes=[AllowAny]

class UserUpdateView(RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]






class UserDeleteView(DestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserListSerializer
    permission_classes=[IsAuthenticated]

class UserDetailView(RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserRetrieveSerializer
    permission_classes=[IsAuthenticated]
    # lookup_field = 'user'
    # lookup_url_kwarg = "abc"


class ChurchDetailView(RetrieveAPIView):
    queryset = ChurchDetails.objects.all()
    serializer_class = ChurchAddUpdateSerializer
    # permission_classes = [IsAdminUser]

class ChurchEditView(RetrieveUpdateAPIView):
    queryset = ChurchDetails.objects.all()
    serializer_class = ChurchAddUpdateSerializer
    permission_classes = [IsAdminUser]


class PostsViewset(viewsets.ModelViewSet):
    serializer_class = FileUploadSerializer
    parser_classes = (MultipartJsonParser, parsers.JSONParser)
    queryset = FileUpload.objects.all()
    # lookup_field = 'id'

class OtpVerifyViewSet(CreateAPIView):
    queryset = OtpModels.objects.all()
    serializer_class = OTPVeifySerializer
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data.get("otp", None)
        try:
            otp_obj = OtpModels.objects.get(otp=otp)
            if (datetime.now(timezone.utc) - otp_obj.created_time).total_seconds() >= 1800:
                otp_obj.is_expired = True
                otp_obj.save()
                return Response({'success': False,'message': 'Otp Expired'}, status=HTTP_400_BAD_REQUEST)
            if otp_obj.is_expired:
                return Response({'success': False,'message': 'Otp Already Used'}, status=HTTP_400_BAD_REQUEST)
        except:
            return Response({'success': False,'message': 'Invalid Otp'}, status=HTTP_400_BAD_REQUEST)
        else:
            otp_obj.is_expired = True
            otp_obj.save()
            return Response({'success': True,'message':'OTP Verified Successfully'}, status=HTTP_201_CREATED)


class SecondaryaddView(CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = SecondaryaddSerializer
    permission_classes=[IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = self.kwargs['pk']
        secondary_users = serializer.validated_data.get('secondary_user',None)
        try:
            if secondary_users:
                user_instance = UserProfile.objects.get(id=user_id) 
                if user_instance.is_primary == True:
                    for secondary_user in secondary_users:
                        sec_user = FileUpload.objects.get(id=secondary_user.id)
                        user_instance.secondary_user.add(sec_user)
                    total_count = user_instance.secondary_user.count()
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
    # permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prayer_id = self.kwargs['pk']
        prayer_profiles = serializer.validated_data.get('user_profile',None)
        try:
            if prayer_profiles:   
                prayer_instance = PrayerGroup.objects.get(id=prayer_id) 
                for prayer_profile in prayer_profiles:
                    member_user = FileUpload.objects.get(id=prayer_profile.id)
                    prayer_instance.user_profile.add(member_user)
                return Response({'success': True,'message':'Group member Added Successfully'}, status=HTTP_201_CREATED)
            else:
                return Response({'success': False,'message': 'Something Went Wrong'}, status=HTTP_400_BAD_REQUEST)
        except:
            return Response({'success': False,'message': 'Something Went Wrong'}, status=HTTP_400_BAD_REQUEST)




