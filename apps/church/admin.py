from django.contrib import admin
# from import_export.signals import post_import, post_export

# Register your models here.
from apps.church.models import NoticeBereavement, Members, UserProfile, PrayerGroup, Notice, Family, ChurchDetails, \
    OtpModels, FileUpload, Notification, Images, Occupation, MemberType, NoticeReadSecondary, NoticeReadPrimary, \
    NoticeReadAdmin, ViewRequestNumber,PrivacyPolicy,PhoneVersion

from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.http import HttpResponse
import csv
class FileAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    actions = ['download_csv']

    def download_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    download_csv.short_description = "Download CSV file for selected profiles."


class MemeberAdmin(admin.ModelAdmin):
    search_fields = ('name',)

admin.site.register(UserProfile)
admin.site.register(PrayerGroup)
admin.site.register(Family)
admin.site.register(Notice)
admin.site.register(ChurchDetails)
admin.site.register(OtpModels)
admin.site.register(Notification)
admin.site.register(Images)
admin.site.register(FileUpload,FileAdmin)
admin.site.register(Members,MemeberAdmin)
admin.site.register(NoticeBereavement)
admin.site.register(Occupation)
admin.site.register(MemberType)
admin.site.register(NoticeReadPrimary)
admin.site.register(NoticeReadSecondary)
admin.site.register(NoticeReadAdmin)
admin.site.register(ViewRequestNumber)
admin.site.register(PrivacyPolicy)
admin.site.register(PhoneVersion)
