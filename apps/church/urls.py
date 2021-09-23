from django.urls import include, path
from django.conf.urls import url
from . import views
from rest_framework.routers import DefaultRouter
from apps.api.views import UserNoticeList, NoticeBereavementDelete, NoticeBereavementEdit, NoticeBereavementCreate, \
    FamilyDetailView, PrayerGroupBasedFamilyView, PrayerGrouplistView, ChurchVicarView, \
    ChurchHistoryView, ChurchImagesView, PrayerGroupaddView, PrayerGroupMemberaddView, \
    FamilyListView, FamilyMemberList, NoticeModelViewSet, SendOtp, PrayerGroupBasedMembersView, FamilyMemberDetails, \
    ViewRequestNumberViewset, AcceptViewRequestNumberViewset, EachUserNotification, EachUserUnreadCount, PrivacyView, \
    PhoneVersionView, GalleryImagesView, GalleryImagesCreateView, SendOtpSecSave, FamilyListPaginatedView,\
    PrayerGroupBasedFamilyPaginatedView,PrayerGroupBasedMembersPaginatedView,SendWithoutOtpSecSave, UpdatePhoneNumberSecondary,\
    PrimaryToSecondaryViewset,PrimaryNumberChangeViewset,ChurchVicarEditView,ChurchHistoryEditView,DeviceInactiveView,RegisteredUsersViewAdmin,\
    UnRegisteredUsersViewAdmin,HomeViewAdmin,UserStatisticsViewAdmin,ChangeRequestModelViewSet,VicarsViewSet,StatusChangeViewset,\
    AnniversaryAndBirthdays, UpcomingAnniversaryAndBirthdays
from push_notifications.api.rest_framework import APNSDeviceAuthorizedViewSet, GCMDeviceAuthorizedViewSet
router = DefaultRouter()

# Notice APIs
router.register(r'notices', NoticeModelViewSet)
router.register(r'change-request', ChangeRequestModelViewSet)
router.register(r'phone-version', PhoneVersionView)
router.register(r'occupations', views.OccupationView)
router.register(r'member-types', views.MemberTypeView)
router.register(r'images-category',GalleryImagesView,basename='gallery_images')
router.register(r'gallery-image-upload-admin',GalleryImagesCreateView,basename='gallery_image_upload_admin')
router.register(r'church-vicar-edit',ChurchVicarEditView,basename='church_vicar_edit')
router.register(r'church-vicars',VicarsViewSet,basename='church_vicars')
router.register(r'church-history-edit',ChurchHistoryEditView,basename='church_history_edit')
router.register(r'device/apns', APNSDeviceAuthorizedViewSet)
router.register(r'device/gcm', GCMDeviceAuthorizedViewSet)
#router.register(r'registered-users',RegisteredUsersViewAdmin,basename='users-lists')
#router.register(r'unregistered-users',UnRegisteredUsersViewAdmin,basename='unreg-users-lists')

urlpatterns = [
    path('', views.UserListView.as_view()),
    path('admin/', include(router.urls)),
    path('create-prayer-group/',PrayerGroupaddView.as_view(),name='create_user'),
    path('create-bereavementnotice/',NoticeBereavementCreate.as_view(),name='create_bereavement'),
    url(r'^(?P<pk>[\w-]+)/edit-bereavementnotice/',NoticeBereavementEdit.as_view(),name='edit_bereavement'),
    url(r'^(?P<pk>[\w-]+)/delete-bereavementnotice/',NoticeBereavementDelete.as_view(),name='delete_bereavement'),
    path('prayer-group-list/',PrayerGrouplistView.as_view(),name='prayer_group_list'),
    path('notice-lists/',UserNoticeList.as_view(),name='notice_lists'),
    # Family APIs
    path('family-lists/',FamilyListView.as_view(),name='family_lists'),
    path('family-lists-paginated/',FamilyListPaginatedView.as_view(),name='family_lists_paginated'),
    url(r'^family-member-list/(?P<pk>\d+)/$',FamilyMemberList.as_view(),name='family_member_list'),
    url(r'^prayer-group-based-family-group-list/(?P<pk>\d+)/$',PrayerGroupBasedFamilyView.as_view(),name='prayer_group_list'),
    url(r'^prayer-group-based-member-list/(?P<pk>\d+)/$',PrayerGroupBasedMembersView.as_view(),name='prayer_group_member_list'),

    url(r'^prayer-group-based-family-group-list-paginated/(?P<pk>\d+)/$',PrayerGroupBasedFamilyPaginatedView.as_view(),name='prayer_group_list_paginated'),
    url(r'^prayer-group-based-member-list-paginated/(?P<pk>\d+)/$',PrayerGroupBasedMembersPaginatedView.as_view(),name='prayer_group_member_list_paginated'),
    url(r'^family-detail/(?P<pk>\d+)/$',FamilyDetailView.as_view(),name='family_detail'),

    url(r'^(?P<pk>[\w-]+)/church-vicar-details/$',ChurchVicarView.as_view(),name='church_vicar'),
    url(r'^(?P<pk>[\w-]+)/church-details/$',ChurchHistoryView.as_view(),name='church_history'),
    url(r'^(?P<pk>[\w-]+)/church-images-details/$',ChurchImagesView.as_view(),name='church_images'),
    url(r'^(?P<pk>[\w-]+)/add-members/$',PrayerGroupMemberaddView.as_view(),name='add_members'),
    
    # Generate OTP
    url(r'^get-otp/$',SendOtp.as_view(),name='send_otp'),
    url(r'^get-otp-user-save/$',SendOtpSecSave.as_view(),name='send_otp'),
    url(r'^get-without-otp-user-save/$',SendWithoutOtpSecSave.as_view(),name='send_without_otp'),

    url(r'^family-member-details/$',FamilyMemberDetails.as_view(),name='family_member_details'),
    url(r'^notification-status/$',EachUserNotification.as_view(),name='notification_detail'),
    url(r'^notification-unread-count/$',EachUserUnreadCount.as_view(),name='notification_unread_detail'),
    url(r'^number-request/$',ViewRequestNumberViewset.as_view(),name='number_request'),
    url(r'^number-request-accept/$',AcceptViewRequestNumberViewset.as_view(),name='number_request_accept'),
    path('privacy-policy/',PrivacyView.as_view(),name='privacy'),
    path('update-phone-number-secondary/', UpdatePhoneNumberSecondary.as_view(),name='update-phone-number-secondary'),
    url(r'^primary-to-secondary/$',PrimaryToSecondaryViewset.as_view(),name='primary_to_secondary'),
    url(r'^status-change/$',StatusChangeViewset.as_view(),name='status_change'),
    url(r'^change-phone-number-primary/$',PrimaryNumberChangeViewset.as_view(),name='change_phone_number_primary'),
    url(r'^device-inactive/$',DeviceInactiveView.as_view(),name='device_inactive'),
    url(r'^registered-users/$',RegisteredUsersViewAdmin.as_view(),name='registered-users'),
    url(r'^unregistered-users/$',UnRegisteredUsersViewAdmin.as_view(),name='unregistered-users'),
    url(r'^home/$',HomeViewAdmin.as_view(),name='home'),
    url(r'^user-statistics/$',UserStatisticsViewAdmin.as_view(),name='user_statistics'),
    url(r'^anniversary-birthday/$', AnniversaryAndBirthdays.as_view(),name='anniversary-birthday'),
    url(r'^upcoming-anniversary-birthday/$', UpcomingAnniversaryAndBirthdays.as_view(),name='upcoming-anniversary-birthday'),
    
    

]

