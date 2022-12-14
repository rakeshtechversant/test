from django.urls import include, path
from django.conf.urls import url

from apps.api.views import UserLoginView, UserLoginMobileView, UserListView, UserDetailView, UserDeleteView, \
    UserUpdateView, UserCreateView, PostsViewset, \
    OtpVerifyViewSet, SecondaryaddView, Profile, UnapprovedMemberView, UpdateMemberByPrimary, CreateUserByAdminView, \
    UpdateUserByAdminView, AddFamilyByAdminView, GalleryImagesView, UpdateFamilyByPrimary, OtpVerifyUserIdViewSet, \
    UserLoginMobileWithOutOtpView,UserListCommonView,OtpVerifyUserCheckNumberViewSet,StatusChangeAcceptView,PrimaryNumberChangeAcceptView,\
    AdminRequestSectionView,UserDetailViewPage,UserDownloadView,CreateMemoryUserView,CreateFamilyMemoryUserView,UpdateUserByMembersView, OfflineChangesByAdminView, UserRegisterView

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'excel-import', PostsViewset, basename='excel_import')
router.register(r'seconday-member-by-primary', UnapprovedMemberView, basename='seconday-member-by-primary')
router.register(r'status-change-accept-reject', StatusChangeAcceptView, basename='status-change-accept-reject')
router.register(r'primary-number-accept-reject', PrimaryNumberChangeAcceptView, basename='primary-number-change-accept-reject')
router.register(r'^admin-requests-list',AdminRequestSectionView,basename='admin_requests_list'),
router.register(r'csv-download',UserDownloadView,basename='csv-download'),

urlpatterns = [
    path('login-user/', UserLoginView.as_view(),name='login'),
    path('register/', UserRegisterView.as_view(),name='register_user'),
    path('create/',UserCreateView.as_view(),name='create_user'),
    path('mobile-login/',UserLoginMobileView.as_view(),name='create_user_mobile'),
    path('mobile-login-without-otp/',UserLoginMobileWithOutOtpView.as_view(),name='create_user_mobile'),
    path('sec_member/',UserListView.as_view(),name='user_list'),
    path('sec_member_paginated/',UserListCommonView.as_view(),name='user_list_paginated'),

    path('otp_verify/',OtpVerifyViewSet.as_view(),name='otp_verify'),
    path('otp_verify_id/',OtpVerifyUserIdViewSet.as_view(),name='otp_verify_id'),
    path('otp_verify_check/',OtpVerifyUserCheckNumberViewSet.as_view(),name='otp_verify_check'),
    path('profile/',Profile.as_view(), name='profile'),
    path('user-by-admin/', CreateUserByAdminView.as_view(), name='user_by_admin'),
    path('create-memory-user/', CreateMemoryUserView.as_view(), name='create_memory_user'),
    path('create-memory-user-from-family/', CreateFamilyMemoryUserView.as_view(), name='create_memory_user_from_family'),

    path('update-user-by-admin/<int:pk>/', UpdateUserByAdminView.as_view(), name='update_user_by_admin'),
    path('add-family-by-admin/<int:pk>/', AddFamilyByAdminView.as_view(), name='add_family_by_admin'),
    path('add-family-by-admin/', AddFamilyByAdminView.as_view(), name='add_family_by_admin'),
    path('update-family-by-primary/', UpdateFamilyByPrimary.as_view(), name='update-family-by-primary'),
    path('update-user-by-family-members/<int:pk>/', UpdateUserByMembersView.as_view(), name='update_user_by_family_members'),

    url(r'^(?P<pk>[\w-]+)/$',UserDetailView.as_view(),name='ind_user'),
    url(r'^apis/(?P<pk>[\w-]+)/$',UserDetailViewPage.as_view(),name='ind_user'),
    url(r'^update-member-own/$',UserUpdateView.as_view(),name='update_user'),
    url(r'^(?P<pk>[\w-]+)/add-users/$',SecondaryaddView.as_view(),name='add_user'),
    url(r'^(?P<pk>[\w-]+)/delete/$',UserDeleteView.as_view(),name='delete_user'),
    
    url(r'^update-member-by-primary/(?P<pk>[\w-]+)/$', UpdateMemberByPrimary.as_view(),name='update_member_by_primary'),
    url(r'^api/', include(router.urls)),
    path('offline-changes-by-admin/', OfflineChangesByAdminView.as_view(), name='offline_changes_by_admin'),

]
