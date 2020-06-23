import csv
import random
import string
import datetime

from django.core.management.base import BaseCommand, CommandError
from apps.church.models import ChurchVicars


class Command(BaseCommand):
    def handle(self, *args, **options):
        f = open('apps/api/csv_tables/vicars.csv', 'r')
        data = csv.reader(f)
        for index, row in enumerate(data):
            if index == 0:
                continue
            if (row[0] != ''):
                vicar_name= row[1]
                start_year= row[2]
                end_year= row[3]
                vicar_info= row[4]
                vicar_type= row[5]
                p, created = ChurchVicars.objects.get_or_create(vicar_name=vicar_name,start_year=start_year,\
                    end_year=end_year,vicar_info=vicar_info,vicar_type=vicar_type)
            else:
                pass
                print ('exit')



