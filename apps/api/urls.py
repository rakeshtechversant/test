from django.urls import include, path
from django.conf.urls import url

from apps.api.views import UserRegistrationMobileView,UserListView,UserDetailView,UserDeleteView,UserUpdateView,UserCreateView,PostsViewset,OtpVerifyViewSet,SecondaryaddView
from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'excel-import', PostsViewset, basename='excel_import')
urlpatterns = [
    path('rest-auth/', include('rest_auth.urls')),
    path('create/',UserCreateView.as_view(),name='create_user'),
    path('mobile/',UserRegistrationMobileView.as_view(),name='create_user_mobile'),
    path('lists/',UserListView.as_view(),name='user_list'),
    path('otp_verify/',OtpVerifyViewSet.as_view(),name='otp_verify'),
    url(r'^(?P<pk>[\w-]+)/$',UserDetailView.as_view(),name='ind_user'),
    url(r'^(?P<pk>[\w-]+)/edit/$',UserUpdateView.as_view(),name='update_user'),
    url(r'^(?P<pk>[\w-]+)/add-users/$',SecondaryaddView.as_view(),name='add_user'),
    url(r'^(?P<pk>[\w-]+)/delete/$',UserDeleteView.as_view(),name='delete_user'),
    url(r'^api/', include(router.urls)),

]
