from django.contrib import admin
# from import_export.signals import post_import, post_export

# Register your models here.
from apps.church.models import UserProfile,PrayerGroup,Notice,Family,ChurchDetails,OtpModels,FileUpload,Notification,Images
from import_export.admin import ImportExportModelAdmin
from import_export import resources

@admin.register(FileUpload)

class ViewAdmin(ImportExportModelAdmin):
    fields=('user','first_name','last_name','dob','date_of_marriage','address','occupation','about','profile_image','mobile_number')
    export_order =('user','first_name','last_name','dob','date_of_marriage','address','occupation','about','profile_image','mobile_number')
    import_id_fields =('user','first_name','last_name','dob','date_of_marriage','address','occupation','about','profile_image','mobile_number')


admin.site.register(UserProfile)
admin.site.register(PrayerGroup)
admin.site.register(Family)
admin.site.register(Notice)
admin.site.register(ChurchDetails)
admin.site.register(OtpModels)
admin.site.register(Notification)
admin.site.register(Images)
