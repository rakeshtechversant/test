from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from . import models

class UserSerializer(serializers.ModelSerializer):


    User.email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=models.User.objects.all())]
            )
    User.username = serializers.CharField(
            validators=[UniqueValidator(queryset=models.User.objects.all())]
            )
    User.password = serializers.CharField(min_length=8)

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'],
             validated_data['password'])
        user_profile = models.UserProfile.objects.create_user(user=user)
        return user_profile.user

    class Meta:
        model = models.UserProfile
        fields = ('user', 'is_primary','key' )




class FamilySerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Family
		fields = ('name','members_length')
