from django.contrib import admin
# from import_export.signals import post_import, post_export

# Register your models here.
from apps.church.models import NoticeBereavement, Members, UserProfile, PrayerGroup, Notice, Family, ChurchDetails, \
    OtpModels, FileUpload, Notification, Images, Occupation, MemberType, NoticeReadSecondary, NoticeReadPrimary, \
    NoticeReadAdmin, ViewRequestNumber,PrivacyPolicy,PhoneVersion

from import_export import resources
from import_export.admin import ImportExportModelAdmin, ImportMixin, ExportMixin, ImportExportMixin
from django.http import HttpResponse
import csv


class FileUploadResource(resources.ModelResource):
    class Meta:
        model = FileUpload
        exclude = ('id' )
        import_id_fields = ['primary_user_id']

class FileAdmin(ImportExportModelAdmin):
    list_display = ('name', 'phone_no_primary')
    search_fields = ['name','phone_no_primary']
    resource_class = FileUploadResource

    # actions = ['download_csv']

    # def download_csv(self, request, queryset):
    #     meta = self.model._meta
    #     field_names = [field.name for field in meta.fields]

    #     response = HttpResponse(content_type='text/csv')
    #     response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
    #     writer = csv.writer(response)

    #     writer.writerow(field_names)
    #     for obj in queryset:
    #         row = writer.writerow([getattr(obj, field) for field in field_names])

    #     return response

    # download_csv.short_description = "Download CSV file for selected profiles."

class MemberResource(resources.ModelResource):
    class Meta:
        model = Members
        exclude = ('id' )
        import_id_fields = ['secondary_user_id']

class MemeberAdmin(ImportExportModelAdmin):
    list_display = ('member_name','phone_no_secondary_user')
    search_fields = ['member_name','phone_no_secondary_user']

class ImageAdmin(admin.ModelAdmin):
    list_display = ('id','image','category','title')
    search_fields = ['image','category','title']

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('created_by_admin','created_by_primary','created_by_secondary','message')
    search_fields = ['created_by_admin','created_by_primary','created_by_secondary','message']

class OccupationAdmin(admin.ModelAdmin):
    list_display = ('occupation',)
    search_fields = ['occupation',]

class FamilyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name',]

admin.site.register(UserProfile)
admin.site.register(PrayerGroup)
admin.site.register(Family,FamilyAdmin)
admin.site.register(Notice)
admin.site.register(ChurchDetails)
admin.site.register(OtpModels)
admin.site.register(Notification,NotificationAdmin)
admin.site.register(Images,ImageAdmin)
admin.site.register(FileUpload,FileAdmin)
admin.site.register(Members,MemeberAdmin)
admin.site.register(NoticeBereavement)
admin.site.register(Occupation,OccupationAdmin)
admin.site.register(MemberType)
admin.site.register(NoticeReadPrimary)
admin.site.register(NoticeReadSecondary)
admin.site.register(NoticeReadAdmin)
admin.site.register(ViewRequestNumber)
admin.site.register(PrivacyPolicy)
admin.site.register(PhoneVersion)

