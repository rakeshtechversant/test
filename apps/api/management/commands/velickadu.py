import csv
import random
import string
import datetime

from django.core.management.base import BaseCommand, CommandError
from apps.church.models import FileUpload , Family, Members , PrayerGroup


class Command(BaseCommand):
    def handle(self, *args, **options):
        f = open('apps/api/csv_tables/velickadu.csv', 'r')
        data = csv.reader(f)
        church = None
        for index, row in enumerate(data):
            if index == 0:
                continue
            if (( row[3] == '') and (row[8] != '')):
                members= row[8]
                relation= row[9]
                dob= row[11]
                dom = row[12]
                members = Members.objects.create(member_name=members,relation=relation,primary_user_id=church,dob=dob,dom=dom)

            elif( row[3] != ''):
                prayer_group = row[1]
                user_id = row[2]
                name = row[3]
                house_name= row[4]
                address= row[5]
                phone_no_primary= row[6]
                phone_no_secondary= row[7]
                dob= row[11]
                dom = row[12]
                blood_group= row[13]
                email= row[14]
                church = FileUpload.objects.create(name=name,address=address,phone_no_primary=phone_no_primary,phone_no_secondary=phone_no_secondary,dob=dob,dom=dom,blood_group=blood_group,email=email)
                Family.objects.create(name=house_name,primary_user_id=church)
                pg_obj,created = PrayerGroup.objects.get_or_create(name=prayer_group)
                pg_obj.primary_user_id.add(church.pk)
            else:
                pass
                print ('exit')



