from django.urls import include, path
from django.conf.urls import url

from apps.api.views import UserLoginView, UserLoginMobileView, UserListView, UserDetailView, UserDeleteView, \
    UserUpdateView, UserCreateView, PostsViewset, \
    OtpVerifyViewSet, SecondaryaddView, Profile, UnapprovedMemberView, UpdateMemberByPrimary, CreateUserByAdminView, \
    UpdateUserByAdminView, AddFamilyByAdminView, GalleryImagesView, UpdateFamilyByPrimary, OtpVerifyUserIdViewSet, \
    UserLoginMobileWithOutOtpView
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'excel-import', PostsViewset, basename='excel_import')
router.register(r'seconday-member-by-primary', UnapprovedMemberView, basename='seconday-member-by-primary')
urlpatterns = [
    path('login-user/', UserLoginView.as_view(),name='login'),
    path('create/',UserCreateView.as_view(),name='create_user'),
    path('mobile-login/',UserLoginMobileView.as_view(),name='create_user_mobile'),
    path('mobile-login-without-otp/',UserLoginMobileWithOutOtpView.as_view(),name='create_user_mobile'),
    path('sec_member/',UserListView.as_view(),name='user_list'),
    path('otp_verify/',OtpVerifyViewSet.as_view(),name='otp_verify'),
    path('otp_verify_id/',OtpVerifyUserIdViewSet.as_view(),name='otp_verify_id'),
    path('profile/',Profile.as_view(), name='profile'),
    path('user-by-admin/', CreateUserByAdminView.as_view(), name='user_by_admin'),
    path('update-user-by-admin/<int:pk>/', UpdateUserByAdminView.as_view(), name='update_user_by_admin'),
    path('add-family-by-admin/<int:pk>/', AddFamilyByAdminView.as_view(), name='add_family_by_admin'),
    path('add-family-by-admin/', AddFamilyByAdminView.as_view(), name='add_family_by_admin'),
    path('update-family-by-primary/', UpdateFamilyByPrimary.as_view(), name='update-family-by-primary'),

    url(r'^(?P<pk>[\w-]+)/$',UserDetailView.as_view(),name='ind_user'),
    url(r'^update-member-own/$',UserUpdateView.as_view(),name='update_user'),
    url(r'^(?P<pk>[\w-]+)/add-users/$',SecondaryaddView.as_view(),name='add_user'),
    url(r'^(?P<pk>[\w-]+)/delete/$',UserDeleteView.as_view(),name='delete_user'),

    url(r'^update-member-by-primary/(?P<pk>[\w-]+)/$', UpdateMemberByPrimary.as_view(),name='update-member-by-primary'),

    url(r'^api/', include(router.urls)),

]
