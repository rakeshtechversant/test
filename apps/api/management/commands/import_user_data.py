import csv
from django.core.management.base import BaseCommand
from apps.church.models import FileUpload, Family, Members, PrayerGroup


class Command(BaseCommand):
    def handle(self, *args, **options):
        f = open('production_data.csv', 'r')
        data = csv.reader(f, delimiter=',')
        for index, row in enumerate(data):
            if index == 0:
                continue

            try:
                name = row[1]
                membership_id = row[3]
                prayer_group_name = row[4]
                phone_no_primary = row[5]
                phone_no_secondary = row[6]
                current_address = row[8]
                residential_address = row[9]
                permanent_address = row[10]
                parish_name = row[11]
                dob = row[12]
                dom = row[13]
                blood_group = row[14]
                email = row[7]

                primary_user = FileUpload.objects.create(name=name,
                                                   phone_no_primary=phone_no_primary,
                                                   phone_no_secondary=phone_no_secondary,
                                                   current_address=current_address,
                                                   residential_address=residential_address,
                                                   permanent_address=permanent_address,
                                                   parish_name=parish_name,
                                                   dob=dob,
                                                   dom=dom,
                                                   blood_group=blood_group,
                                                   email=email)

                family = Family.objects.create(name=membership_id,
                                                primary_user_id=primary_user)

                prayer_group = PrayerGroup.objects.get_or_create(name=prayer_group_name)
                prayer_group[0].family.add(family)
                prayer_group[0].primary_user_id.add(primary_user)

                if row[15]:
                    name = row[15]
                    relation = row[16]
                    dob = row[17]
                    blood_group = row[18]
                    phone_no_secondary_user = row[19]
                    email = row[20]

                    secondary_user = Members.objects.create(member_name=name,
                                                     relation=relation,
                                                     primary_user_id=primary_user,
                                                     dob=dob,
                                                     current_address=current_address,
                                                     residential_address=residential_address,
                                                     permanent_address=permanent_address,
                                                     parish_name=parish_name,
                                                     phone_no_secondary_user=phone_no_secondary_user,
                                                     blood_group=blood_group,
                                                     email=email)
                    prayer_group[0].sec_member.add(secondary_user)

                    if row[21]:
                        name = row[21]
                        relation = row[22]
                        dob = row[23]
                        blood_group = row[24]
                        phone_no_secondary_user = row[25]
                        email = row[26]

                        secondary_user = Members.objects.create(member_name=name,
                                                                relation=relation,
                                                                primary_user_id=primary_user,
                                                                dob=dob,
                                                                current_address=current_address,
                                                                residential_address=residential_address,
                                                                permanent_address=permanent_address,
                                                                parish_name=parish_name,
                                                                phone_no_secondary_user=phone_no_secondary_user,
                                                                blood_group=blood_group,
                                                                email=email)
                        prayer_group[0].sec_member.add(secondary_user)

                    if row[27]:
                        name = row[27]
                        relation = row[28]
                        dob = row[29]
                        blood_group = row[30]
                        phone_no_secondary_user = row[31]
                        email = row[32]

                        secondary_user = Members.objects.create(member_name=name,
                                                                relation=relation,
                                                                primary_user_id=primary_user,
                                                                dob=dob,
                                                                current_address=current_address,
                                                                residential_address=residential_address,
                                                                permanent_address=permanent_address,
                                                                parish_name=parish_name,
                                                                phone_no_secondary_user=phone_no_secondary_user,
                                                                blood_group=blood_group,
                                                                email=email)
                        prayer_group[0].sec_member.add(secondary_user)

                        if row[33]:
                            name = row[33]
                            relation = row[34]
                            dob = row[35]
                            blood_group = row[36]
                            phone_no_secondary_user = row[37]
                            email = row[38]

                            secondary_user = Members.objects.create(member_name=name,
                                                                    relation=relation,
                                                                    primary_user_id=primary_user,
                                                                    dob=dob,
                                                                    current_address=current_address,
                                                                    residential_address=residential_address,
                                                                    permanent_address=permanent_address,
                                                                    parish_name=parish_name,
                                                                    phone_no_secondary_user=phone_no_secondary_user,
                                                                    blood_group=blood_group,
                                                                    email=email)
                            prayer_group[0].sec_member.add(secondary_user)

                        if row[39]:
                            name = row[39]
                            relation = row[40]
                            dob = row[41]
                            blood_group = row[42]
                            phone_no_secondary_user = row[43]
                            email = row[44]

                            secondary_user = Members.objects.create(member_name=name,
                                                                    relation=relation,
                                                                    primary_user_id=primary_user,
                                                                    dob=dob,
                                                                    current_address=current_address,
                                                                    residential_address=residential_address,
                                                                    permanent_address=permanent_address,
                                                                    parish_name=parish_name,
                                                                    phone_no_secondary_user=phone_no_secondary_user,
                                                                    blood_group=blood_group,
                                                                    email=email)
                            prayer_group[0].sec_member.add(secondary_user)

                        if row[45]:
                            name = row[45]
                            relation = row[46]
                            dob = row[47]
                            blood_group = row[48]
                            phone_no_secondary_user = row[49]
                            email = row[50]

                            secondary_user = Members.objects.create(member_name=name,
                                                                    relation=relation,
                                                                    primary_user_id=primary_user,
                                                                    dob=dob,
                                                                    current_address=current_address,
                                                                    residential_address=residential_address,
                                                                    permanent_address=permanent_address,
                                                                    parish_name=parish_name,
                                                                    phone_no_secondary_user=phone_no_secondary_user,
                                                                    blood_group=blood_group,
                                                                    email=email)
                            prayer_group[0].sec_member.add(secondary_user)

                        if row[51]:
                            name = row[51]
                            relation = row[52]
                            dob = row[53]
                            blood_group = row[54]
                            phone_no_secondary_user = row[55]
                            email = row[56]

                            secondary_user = Members.objects.create(member_name=name,
                                                                    relation=relation,
                                                                    primary_user_id=primary_user,
                                                                    dob=dob,
                                                                    current_address=current_address,
                                                                    residential_address=residential_address,
                                                                    permanent_address=permanent_address,
                                                                    parish_name=parish_name,
                                                                    phone_no_secondary_user=phone_no_secondary_user,
                                                                    blood_group=blood_group,
                                                                    email=email)
                            prayer_group[0].sec_member.add(secondary_user)

                        if row[57]:
                            name = row[57]
                            relation = row[58]
                            dob = row[59]
                            blood_group = row[60]
                            phone_no_secondary_user = row[61]
                            email = row[62]

                            secondary_user = Members.objects.create(member_name=name,
                                                                    relation=relation,
                                                                    primary_user_id=primary_user,
                                                                    dob=dob,
                                                                    current_address=current_address,
                                                                    residential_address=residential_address,
                                                                    permanent_address=permanent_address,
                                                                    parish_name=parish_name,
                                                                    phone_no_secondary_user=phone_no_secondary_user,
                                                                    blood_group=blood_group,
                                                                    email=email)
                            prayer_group[0].sec_member.add(secondary_user)
            except Exception as e:
                print(str(e))
                pass
        print("Completed")
