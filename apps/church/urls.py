from django.urls import include, path
from django.conf.urls import url
from . import views
from apps.api.views import ChurchDetailView,ChurchEditView,PrayerGroupaddView,PrayerGroupMemberaddView,FamilyListView
urlpatterns = [
    path('', views.UserListView.as_view()),
    url(r'^(?P<pk>[\w-]+)/church-details/$',ChurchDetailView.as_view(),name='create_user'),
    path('create-prayer-group/',PrayerGroupaddView.as_view(),name='create_user'),
    url(r'^(?P<pk>[\w-]+)/edit/$',ChurchEditView.as_view(),name='update_church'),
    url(r'^(?P<pk>[\w-]+)/add-members/$',PrayerGroupMemberaddView.as_view(),name='add_members'),
    path('family-lists/',FamilyListView.as_view(),name='family_lists'),
]

