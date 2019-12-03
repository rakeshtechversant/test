import csv
import os
import random
import string
import datetime
from django.http import HttpResponse
from django.core.management.base import BaseCommand, CommandError
from apps.church.models import FileUpload , Family, Members , PrayerGroup 
from pathlib import Path


class Command(BaseCommand):
    def handle(self, *args, **options):
        import pdb;pdb.set_trace()
        path_to_download_folder = str(os.path.join(Path.home(), "Downloads"))
        with open(path_to_download_folder+'/myfiles.csv', 'w', newline="") as myfile:
            writer = csv.writer(myfile)
            primary_qs = FileUpload.objects.all()
            #Header
            writer.writerow(['prayer group','Name','Family_name','Family_About','Family_Image',\
                'Members','Phone_no_primary','Phone_no_secondary','Address','Relation','User_Image',\
                'occupation','About_User'
                # ,'Martial_Status','Memory_Date'
                ])
            for user in primary_qs:
                output1 = []
                output2 = []
                try:
                    user_id = user.primary_user_id
                    prayer_obj = PrayerGroup.objects.get(primary_user_id=user_id)
                    family_obj = Family.objects.get(primary_user_id=user_id)
                    if user.image :
                        img=user.image.url
                    else:
                        img = ''
                    if family_obj.image :
                        img_fam=family_obj.image.url
                    else:
                        img_fam = ''
                    writer.writerows([''])
                    output1.append([prayer_obj.name,user.name,family_obj.name,family_obj.about,img_fam,\
                        '',user.phone_no_primary,user.phone_no_primary,user.address,user.relation,img,\
                        user.occupation,user.about])
                    writer.writerows(output1)
                    print(output1)

                    mem_obj=Members.objects.filter(primary_user_id=user_id)
                    for mem in mem_obj:
                        if mem.image :
                            img_mem=mem.image.url
                        else:
                            img_mem = ''
                        output2.append(['','','','','',mem.member_name,mem.phone_no_secondary_user,mem.phone_no_secondary_user_secondary,'',\
                        	mem.relation,img_mem,mem.occupation,mem.about])
                    writer.writerows(output2)

                except:
                    pass
            print("exit")
            #CSV Data
            
            #File is saved in home directory