import csv
import random
import string
import datetime

from django.core.management.base import BaseCommand, CommandError
from apps.church.models import FileUpload , Family, Members , PrayerGroup


class Command(BaseCommand):
    def handle(self, *args, **options):
        f = open('apps/api/csv_tables/download.csv', 'r')
        data = csv.reader(f, delimiter=',')
        church = None
        # import pdb;pdb.set_trace()
        for index, row in enumerate(data):
            if index == 0:
                continue
            try:
                if (( row[2] == '') and (row[6] != '')):
                    members_name= row[6]
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
                    secondary_user_id = row[19]
                    # import pdb;pdb.set_trace()
                    if(row[19] != ''):
                        members = Members.objects.get(secondary_user_id=secondary_user_id)
                        members.member_name=members_name
                        members.relation=relation
                        members.primary_user_id=church
                        members.dob=dob
                        members.dom=dom
                        members.image=user_image
                        members.phone_no_secondary_user=phone_no_primary
                        members.phone_no_secondary_user_secondary=phone_no_secondary
                        members.blood_group=blood_group
                        members.email=email
                        members.occupation=occupation
                        members.about=about_user
                        members.save()
                    elif(row[19] == ''):
                        members = Members.objects.create(member_name=members_name,relation=relation,primary_user_id=church,\
                            dob=dob,dom=dom,image=user_image,phone_no_secondary_user=phone_no_primary,phone_no_secondary_user_secondary=phone_no_secondary,\
                            blood_group=blood_group,email=email,occupation=occupation,about=about_user)
                    else:
                        pass
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
                    if(row[18] != ''):
                        church = FileUpload.objects.get(primary_user_id=primary_user_id)

                        if church:
                            church.name=name
                            church.image=user_image
                            church.address=address
                            church.phone_no_primary=phone_no_primary
                            church.phone_no_secondary=phone_no_secondary
                            church.dob=dob
                            church.dom=dom
                            church.blood_group=blood_group
                            church.email=email
                            church.occupation=occupation
                            church.about=about_user
                            church.relation=relation
                            church.save()
                        fam_obj = Family.objects.get(primary_user_id=church)
                        if fam_obj:
                            fam_obj.name = family_name
                            fam_obj.about = family_about
                            fam_obj.image = family_image
                            fam_obj.save()

                        # pg_obj = PrayerGroup.objects.get(primary_user_id=primary_user_id)
                        #     pg_obj.name=prayer_group
                        # pg_obj.primary_user_id.add(church.pk)


                    elif(row[18] == ''):
                        church = FileUpload.objects.create(name=name,image=user_image,address=address,phone_no_primary=phone_no_primary,phone_no_secondary=phone_no_secondary,\
                            dob=dob,dom=dom,blood_group=blood_group,email=email,occupation=occupation,about=about_user,relation=relation)
                        fam_obj = Family.objects.create(name=family_name,primary_user_id=church,about=family_about,image=family_image)
                        pg_obj = PrayerGroup.objects.get(name=prayer_group)
                        pg_obj.primary_user_id.add(church.pk)
                    else:
                        pass
                else:
                    pass
            except:
                pass
                print ('exit')



