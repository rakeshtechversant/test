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
        path_to_download_folder = str(os.path.join(str(Path.home()), "Downloads"))
        with open('apps/api/csv_tables/download.csv', 'w', newline="") as myfile:
            writer = csv.writer(myfile, quoting=csv.QUOTE_MINIMAL)
            primary_qs = FileUpload.objects.all()
            #Header
            writer.writerow(['SL NO','PRAYER GROUP','NAME','FAMILY NAME','FAMILY ABOUT','FAMILY IMAGE',\
                'MEMBERS','PHONE NO PRIMARY','PHONE NO SECONDARY','EMAIL','ADDRESS','RELATION','USER IMAGE',\
                'OCCUPATION','ABOUT USER','DOB','DOM','BLOOD GROUP','ID_PRIMARY','ID_SECONDARY'
                # ,'Martial_Status','Memory_Date'
                ])
            count = 1
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
                    output1.append([count,prayer_obj.name,user.name,family_obj.name,family_obj.about,img_fam,\
                        '',user.phone_no_primary,user.phone_no_secondary,user.email,user.address,user.relation,img,\
                        user.occupation,user.about,user.dob,user.dom,user.blood_group,user.primary_user_id,''])
                    writer.writerows(output1)
                    print(output1)
                    count = count + 1
                    try:
                        mem_obj=Members.objects.filter(primary_user_id=user_id)
                        for mem in mem_obj:
                            if mem.image :
                                img_mem=mem.image.url
                            else:
                                img_mem = ''
                            output2.append(['','','','','','',mem.member_name,mem.phone_no_secondary_user,mem.phone_no_secondary_user_secondary,mem.email,'',\
                                mem.relation,img_mem,mem.occupation,mem.about,mem.dob,mem.dom,mem.blood_group,'',mem.secondary_user_id])
                        writer.writerows(output2)
                    except:
                        pass

                except:
                    pass
            print("exit")
            #CSV Data
            
            #File is saved in home directory