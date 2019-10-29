from django.shortcuts import render

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
from apps.api.serializers import FamilyListSerializer,UserRegistrationMobileSerializer,PrayerGroupAddMembersSerializer,PrayerGroupAddSerializer,UserListSerializer,UserRetrieveSerializer,UserCreateSerializer,ChurchAddUpdateSerializer,FileUploadSerializer,OTPVeifySerializer,SecondaryaddSerializer
from apps.church.models import Family,UserProfile,ChurchDetails,FileUpload,OtpModels,PrayerGroup
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST , HTTP_401_UNAUTHORIZED
from django.utils.crypto import get_random_string
from twilio.rest import Client
from church_project import settings


class UserCreateView(CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserCreateSerializer

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
                for userprofile in FileUpload.objects.all():
                    if userprofile.mobile_number == mobile_number:
                        user_count=user_count+1
                    # if not mobile_number:
                    # raise serializers.ValidationError("This field is required")
                        if UserProfile.objects.filter(mobile_number = mobile_number).exists():
                    # raise serializers.ValidationError("This number is already taken")
                            return Response({'message': 'This number is already taken','success':False},status=HTTP_400_BAD_REQUEST)
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
                # raise serializers.ValidationError("We couldn't find your profile in database,Please contact service providers")
                    return Response({'message': 'We couldnt find your profile in database,Please contact service providers','success':False},status=HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message': 'Invalid usertype,Please select again','success':False},status=HTTP_400_BAD_REQUEST)
        except:
        # raise serializers.ValidationError("Invalid usertype,Please select again")
            return Response({'message': 'Something Went Wrong','success':False},status=HTTP_400_BAD_REQUEST)


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
    permission_classes = [IsAdminUser]

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


class SecondaryaddView(RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = SecondaryaddSerializer
    permission_classes=[IsAuthenticated]

class PrayerGroupaddView(CreateAPIView):
    queryset = PrayerGroup.objects.all()
    serializer_class = PrayerGroupAddSerializer
    permission_classes = [IsAdminUser]


class PrayerGroupMemberaddView(RetrieveUpdateAPIView):
    queryset = PrayerGroup.objects.all()
    serializer_class = PrayerGroupAddMembersSerializer
    permission_classes = [IsAdminUser]


