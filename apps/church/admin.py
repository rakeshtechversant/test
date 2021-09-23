from django.contrib import admin
# from import_export.signals import post_import, post_export

# Register your models here.
from apps.church.models import NoticeBereavement, Members, UserProfile, PrayerGroup, Notice, Family, ChurchDetails, \
    OtpModels, FileUpload, Notification, Images, Occupation, MemberType, NoticeReadSecondary, NoticeReadPrimary, \
    NoticeReadAdmin, ViewRequestNumber, PrivacyPolicy, PhoneVersion,PrimaryToSecondary,NumberChangePrimary,UnapprovedMember,\
    ChangeRequest, ChurchVicars

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


class MemberResource(resources.ModelResource):
    class Meta:
        model = Members
        exclude = ('id' )
        import_id_fields = ['secondary_user_id']

class MemeberAdmin(ImportExportModelAdmin):
    list_display = ('member_name','phone_no_secondary_user')
    search_fields = ['member_name','phone_no_secondary_user']


class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'category', 'title')
    search_fields = ['image', 'category', 'title']


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('created_by_admin', 'created_by_primary', 'created_by_secondary', 'message')
    search_fields = ['created_by_admin', 'created_by_primary', 'created_by_secondary', 'message']


class OccupationAdmin(admin.ModelAdmin):
    list_display = ('occupation',)
    search_fields = ['occupation', ]


class FamilyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name', ]

class NoticeAdmin(admin.ModelAdmin):
    list_display = ('notice','created_at')
    search_fields = ['notice',]

class PrayerAdmin(ImportExportModelAdmin):
    list_display = ['name']
    actions = ['export_users']

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def export_users(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['content-Disposition'] = 'attachment; filename="user_data.csv"'
        writer = csv.writer(response)
        prayer_group_name = []
        for i in queryset:
            prayer_group_name.append(i.name)
        if prayer_group_name:
            prayer_obj = PrayerGroup.objects.filter(name__in=prayer_group_name)
            primary_qs = FileUpload.objects.all()
            if primary_qs:
                writer.writerow(['SL NO', 'PRAYER GROUP', 'NAME', 'FAMILY NAME', 'FAMILY ABOUT', 'FAMILY IMAGE', 'MEMBERS',
                                 'RELATION', 'PHONE NO PRIMARY', 'PHONE NO SECONDARY', 'EMAIL', 'ADDRESS', 'USER IMAGE',
                                 'OCCUPATION', 'OCCUPATION DESCRIPTION', 'ABOUT USER', 'DOB', 'DOM', 'BLOOD GROUP',
                                 'MEMORY DATE (YYYY-MM-DD)', 'ID_PRIMARY', 'ID_SECONDARY'
                                 ])
                count = 1
                for prayer_group in prayer_obj:
                    for user in primary_qs:
                        if user.get_file_upload_prayergroup.first().name == prayer_group.name:
                            output1 = []
                            output2 = []
                            try:
                                user_id = user.primary_user_id
                                prayer_obj = PrayerGroup.objects.get(primary_user_id=user_id)
                                family_obj = Family.objects.get(primary_user_id=user_id)
                                if user.image:
                                    img = user.image.url
                                else:
                                    img = ''
                                if family_obj.image:
                                    img_fam = family_obj.image.url
                                else:
                                    img_fam = ''
                                dom = ''
                                try:
                                    if user.marrige_date:
                                        dom = user.marrige_date
                                    elif user.dom:
                                        dom = user.dom
                                    else:
                                        pass
                                except:
                                    dom = ''
                                try:
                                    if user.in_memory_date:
                                        in_memory = str(user.in_memory_date.date())
                                    else:
                                        in_memory = ''
                                except:
                                    in_memory = ''
                                occupation_description = ''
                                occupation = ''
                                if user.occupation:
                                    if user.occupation.split('---'):
                                        occupation = str(user.occupation.split('---')[0])
                                    else:
                                        occupation = ''
                                    try:
                                        if user.occupation.split('---'):
                                            occupation_description = user.occupation.split('---')[1]
                                        else:
                                            occupation_description = ''
                                    except:
                                        pass
                                else:
                                    occupation = ''
                                    occupation_description = ''

                                writer.writerows([''])
                                output1.append([count, prayer_obj.name, user.name, family_obj.name, family_obj.about, img_fam,
                                                '', user.relation, user.phone_no_primary, user.phone_no_secondary, user.email,
                                                user.address, img, occupation, occupation_description, user.about, user.dob,
                                                dom, user.blood_group, in_memory, user.primary_user_id, ''])
                                writer.writerows(output1)
                                count = count + 1
                                try:

                                    mem_obj = Members.objects.filter(primary_user_id=user_id)
                                    for mem in mem_obj:
                                        if mem.image:
                                            img_mem = mem.image.url
                                        else:
                                            img_mem = ''
                                        dom_sec = ''
                                        try:
                                            if mem.marrige_date:
                                                dom_sec = mem.marrige_date
                                            elif mem.dom:
                                                dom_sec = mem.dom
                                            else:
                                                pass
                                        except:
                                            dom_sec = ''
                                        try:
                                            in_memory = str(mem.in_memory_date.date())
                                        except:
                                            in_memory = ''

                                        occupation_description_sec = ''
                                        occupation_sec = ''
                                        if mem.occupation:
                                            if mem.occupation.split('---'):
                                                occupation_sec = str(mem.occupation.split('---')[0])
                                            else:
                                                occupation_sec = ''
                                            try:
                                                if mem.occupation.split('---'):
                                                    occupation_description_sec = mem.occupation.split('---')[1]
                                                else:
                                                    occupation_description_sec = ''
                                            except:
                                                pass
                                        else:
                                            occupation_sec = ''
                                            occupation_description_sec = ''
                                        output2.append(
                                            ['', '', '', '', '', '', mem.member_name, mem.relation, mem.phone_no_secondary_user,
                                             mem.phone_no_secondary_user_secondary, mem.email, '', img_mem, occupation_sec,
                                             occupation_description_sec, mem.about, mem.dob, dom_sec, mem.blood_group,
                                             in_memory, '', mem.secondary_user_id])
                                    writer.writerows(output2)
                                except:
                                    pass

                            except:
                                pass
                return response
    export_users.short_description = 'Export Users In Selected Prayer Groups'

    def export_action(self, request, *args, **kwargs):
        primary_qs = FileUpload.objects.all()
        if primary_qs:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="users_data.csv"'
            writer = csv.writer(response)
            writer.writerow(['SL NO', 'PRAYER GROUP', 'NAME', 'FAMILY NAME', 'FAMILY ABOUT', 'FAMILY IMAGE', 'MEMBERS',
                             'RELATION', 'PHONE NO PRIMARY', 'PHONE NO SECONDARY', 'EMAIL', 'ADDRESS', 'USER IMAGE',
                             'OCCUPATION', 'OCCUPATION DESCRIPTION', 'ABOUT USER', 'DOB', 'DOM', 'BLOOD GROUP',
                             'MEMORY DATE (YYYY-MM-DD)', 'ID_PRIMARY', 'ID_SECONDARY'
                             ])
            count = 1
            for user in primary_qs:
                output1 = []
                output2 = []
                try:
                    user_id = user.primary_user_id
                    prayer_obj = PrayerGroup.objects.get(primary_user_id=user_id)
                    family_obj = Family.objects.get(primary_user_id=user_id)
                    if user.image:
                        img = user.image.url
                    else:
                        img = ''
                    if family_obj.image:
                        img_fam = family_obj.image.url
                    else:
                        img_fam = ''

                    dom = ''
                    try:
                        if user.marrige_date:
                            dom = user.marrige_date
                        elif user.dom:
                            dom = user.dom
                        else:
                            pass
                    except:
                        dom = ''
                    try:
                        in_memory = str(user.in_memory_date.date())
                    except:
                        in_memory = ''

                    occupation_description = ''
                    occupation = ''
                    if user.occupation:
                        if user.occupation.split('---'):
                            occupation = str(user.occupation.split('---')[0])
                        else:
                            occupation = ''
                        try:
                            if user.occupation.split('---'):
                                occupation_description = user.occupation.split('---')[1]
                            else:
                                occupation_description = ''
                        except:
                            pass
                    else:
                        occupation = ''
                        occupation_description = ''
                    writer.writerows([''])
                    output1.append([count, prayer_obj.name, user.name, family_obj.name, family_obj.about, img_fam, '',
                                    user.relation, user.phone_no_primary, user.phone_no_secondary, user.email,
                                    user.address, img, occupation, occupation_description, user.about, user.dob, dom,
                                    user.blood_group, in_memory, user.primary_user_id, ''])
                    writer.writerows(output1)
                    count = count + 1
                    try:
                        mem_obj = Members.objects.filter(primary_user_id=user_id)
                        for mem in mem_obj:
                            if mem.image:
                                img_mem = mem.image.url
                            else:
                                img_mem = ''
                            dom_sec = ''
                            try:
                                if mem.marrige_date:
                                    dom_sec = mem.marrige_date
                                elif mem.dom:
                                    dom_sec = mem.dom
                                else:
                                    pass
                            except:
                                dom_sec = ''
                            try:
                                in_memory = str(mem.in_memory_date.date())
                            except:
                                in_memory = ''

                            occupation_description_sec = ''
                            occupation_sec = ''
                            if mem.occupation:
                                if mem.occupation.split('---'):
                                    occupation_sec = str(mem.occupation.split('---')[0])
                                else:
                                    occupation_sec = ''
                                try:
                                    if mem.occupation.split('---'):
                                        occupation_description_sec = mem.occupation.split('---')[1]
                                    else:
                                        occupation_description_sec = ''
                                except:
                                    pass
                            else:
                                occupation_sec = ''
                                occupation_description_sec = ''

                            output2.append(
                                ['', '', '', '', '', '', mem.member_name, mem.relation, mem.phone_no_secondary_user,
                                 mem.phone_no_secondary_user_secondary, mem.email, '', img_mem, occupation_sec,
                                 occupation_description_sec, mem.about, mem.dob, dom_sec, mem.blood_group, in_memory,
                                 '', mem.secondary_user_id])
                        writer.writerows(output2)
                    except:
                        pass

                except:
                    pass
            return response


admin.site.register(UserProfile)
admin.site.register(PrayerGroup, PrayerAdmin)
admin.site.register(Family, FamilyAdmin)
admin.site.register(Notice,NoticeAdmin)
admin.site.register(ChurchDetails)
admin.site.register(OtpModels)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Images, ImageAdmin)
admin.site.register(FileUpload, FileAdmin)
admin.site.register(Members, MemeberAdmin)
admin.site.register(NoticeBereavement)
admin.site.register(Occupation, OccupationAdmin)
admin.site.register(MemberType)
admin.site.register(NoticeReadPrimary)
admin.site.register(NoticeReadSecondary)
admin.site.register(NoticeReadAdmin)
admin.site.register(ViewRequestNumber)
admin.site.register(PrivacyPolicy)
admin.site.register(PhoneVersion)
admin.site.register(PrimaryToSecondary)
admin.site.register(NumberChangePrimary)
admin.site.register(UnapprovedMember)
admin.site.register(ChangeRequest)
admin.site.register(ChurchVicars)
