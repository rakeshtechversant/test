import csv
import random
import string
import datetime

from django.core.management.base import BaseCommand, CommandError
from apps.church.models import FileUpload , Family, Members , PrayerGroup


class Command(BaseCommand):
    def handle(self, *args, **options):
        f = open('apps/api/csv_tables/download.csv', 'r')
        data = csv.reader(f)
        church = None
        for index, row in enumerate(data):

            if index == 0:
                continue
            try:
                if (( row[2] == '') and (row[6] != '')):
                    members= row[6]
                    phone_no_primary= row[7]
                    phone_no_secondary= row[8]
                    email= row[9]
                    relation= row[11]
                    user_image = row[12]
                    occupation =row[13]
                    about_user =row[14]
                    dob= row[15]
                    dom = row[16]
                    blood_group= row[17]
                    secondary_user_id = row[18]
                    members,created = Members.objects.get_or_create(member_name=members,relation=relation,primary_user_id=church,\
                        dob=dob,dom=dom,image=user_image,phone_no_secondary_user=phone_no_primary,phone_no_secondary_user_secondary=phone_no_secondary,\
                        blood_group=blood_group,email=email,occupation=occupation,about=about_user,secondary_user_id=secondary_user_id)

                elif( row[2] != ''):
                    prayer_group = row[1]
                    # user_id = row[2]
                    name = row[2]
                    family_name= row[3]
                    family_about= row[4]
                    family_image= row[5]


                    phone_no_primary= row[7]
                    phone_no_secondary= row[8]
                    email= row[9]
                    address= row[10]
                    user_image = row[12]
                    occupation = row[13]
                    about_user =row[14]
                    dob= row[15]
                    dom = row[16]
                    blood_group= row[17]
                    primary_user_id= row[18]
                    relation= row[11]
                    church,created = FileUpload.objects.get_or_create(name=name,image=user_image,address=address,phone_no_primary=phone_no_primary,phone_no_secondary=phone_no_secondary,\
                        dob=dob,dom=dom,blood_group=blood_group,email=email,occupation=occupation,about=about_user,relation=relation,primary_user_id=primary_user_id)
                    fam_obj,created = Family.objects.get_or_create(name=family_name,primary_user_id=church,about=family_about,image=family_image)
                    pg_obj,created = PrayerGroup.objects.get_or_create(name=prayer_group)
                    pg_obj.primary_user_id.add(church.pk)
                else:
                    pass
            except:
                pass
                print ('exit')



