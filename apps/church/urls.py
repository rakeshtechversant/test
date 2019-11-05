from django.urls import include, path
from django.conf.urls import url
from . import views
from rest_framework.routers import DefaultRouter
from apps.api.views import PrayerGroupBasedFamilyView, PrayerGrouplistView, ChurchVicarView, \
    ChurchHistoryView, ChurchImagesView, PrayerGroupaddView, PrayerGroupMemberaddView, \
    FamilyListView, FamilyMemberList, NoticeModelViewSet, SendOtp

router = DefaultRouter()

# Notice APIs
router.register(r'notices', NoticeModelViewSet)

urlpatterns = [
    path('', views.UserListView.as_view()),
    path('admin/', include(router.urls)),
    path('create-prayer-group/',PrayerGroupaddView.as_view(),name='create_user'),
    path('prayer-group-list/',PrayerGrouplistView.as_view(),name='prayer_group_list'),
    
    # Family APIs
    path('family-lists/',FamilyListView.as_view(),name='family_lists'),
    url(r'^family-member-list/(?P<pk>\d+)/$',FamilyMemberList.as_view(),name='family_member_list'),
    url(r'^prayer-group-based-family-group-list/(?P<pk>\d+)/$',PrayerGroupBasedFamilyView.as_view(),name='prayer_group_list'),
    # url(r'^prayer-group-based-member-list/(?P<pk>\d+)/$',PrayerGroupBasedMembersView.as_view(),name='prayer_group_member_list'),

    url(r'^(?P<pk>[\w-]+)/church-vicar-details/$',ChurchVicarView.as_view(),name='church_vicar'),
    url(r'^(?P<pk>[\w-]+)/church-details/$',ChurchHistoryView.as_view(),name='church_history'),
    url(r'^(?P<pk>[\w-]+)/church-images-details/$',ChurchImagesView.as_view(),name='church_images'),
    url(r'^(?P<pk>[\w-]+)/add-members/$',PrayerGroupMemberaddView.as_view(),name='add_members'),
    
    # Generate OTP
    url(r'^get-otp/$',SendOtp.as_view(),name='send_otp'),
    

]

