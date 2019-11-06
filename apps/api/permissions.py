from rest_framework.permissions import BasePermission,SAFE_METHODS
from apps.church.models import FileUpload

class IsOwnerOrReadOnly(BasePermission):
    message = 'You must be the owner of the object'
    my_safe_method=['PUT']

    def has_permission(self,request,view):
        if request.method in self.my_safe_method:
            return True
        return False

    def has_object_permission(self,request,view,obj):
        if request.method in self.SAFE_METHODS:
            return True
        return False


class IsPrimaryUserOrReadOnly(BasePermission):

    def has_permission(self,request,view):
        
        if request.method in ['POST', 'PUT', 'PATCH']:
            if  FileUpload.objects.filter(
                phone_no_primary=request.user.username).exists():

                return True
        else:
            return True

        return False


class AdminPermission(BasePermission):

    def has_permission(self,request,view):
        
        if request.user.is_superuser:

            return True
        else:
            return False

        return False






