from django.core.management.base import BaseCommand
from apps.church.models import Members, FileUpload, InactiveUser


class Command(BaseCommand):
    def handle(self, *args, **options):
        primary_users = FileUpload.objects.all()
        secondary_users = Members.objects.all()
        for user in primary_users:
            try:
                inactive_user = InactiveUser()
                inactive_user.name = user.name
                inactive_user.mobile_number = user.phone_no_primary
                inactive_user.membership_id = user.get_file_upload.first().name
                inactive_user.save()
            except Exception as e:
                print(e)
                pass

        for user in secondary_users:
            try:
                inactive_user = InactiveUser()
                inactive_user.name = user.member_name
                inactive_user.mobile_number = user.phone_no_secondary_user
                inactive_user.membership_id = user.primary_user_id.get_file_upload.first().name
                inactive_user.save()
            except Exception as e:
                print(e)
                pass
        print("completed")

