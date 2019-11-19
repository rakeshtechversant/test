from django.shortcuts import render

# Create your views here.

from rest_framework import generics
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

from . import models
from . import serializers

class UserListView(generics.ListAPIView):
    queryset = models.UserProfile.objects.all()
    serializer_class = serializers.UserSerializer

class OccupationView(viewsets.ModelViewSet):
    queryset = models.Occupation.objects.all()
    serializer_class = serializers.OccupationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        data ={
            "success": True,
            'message': "Occupation created"
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


class MemberTypeView(viewsets.ModelViewSet):
    queryset = models.MemberType.objects.all()
    serializer_class = serializers.MemberTypeSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

