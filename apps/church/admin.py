from django.contrib import admin
# from import_export.signals import post_import, post_export

# Register your models here.
from apps.church.models import Members,UserProfile,PrayerGroup,Notice,Family,ChurchDetails,OtpModels,FileUpload,Notification,Images
from import_export.admin import ImportExportModelAdmin
from import_export import resources


admin.site.register(UserProfile)
admin.site.register(PrayerGroup)
admin.site.register(Family)
admin.site.register(Notice)
admin.site.register(ChurchDetails)
admin.site.register(OtpModels)
admin.site.register(Notification)
admin.site.register(Images)
admin.site.register(FileUpload)
admin.site.register(Members)
