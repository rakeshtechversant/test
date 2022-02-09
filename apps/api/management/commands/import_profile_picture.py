from django.core.management.base import BaseCommand
from apps.church.models import Family, Members


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            familys = Family.objects.all()
            for family in familys:
                family_image = family.image
                family.primary_user_id.image = family_image
                family.primary_user_id.save()
                members = Members.objects.filter(primary_user_id=family.primary_user_id)
                for user in members:
                    user.image = family_image
                    user.save()
            print("completed")
        except Exception as e:
            print(str(e))
