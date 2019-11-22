import csv
import random
import string
import datetime

from django.core.management.base import BaseCommand, CommandError
from apps.church.models import Occupation


class Command(BaseCommand):
    def handle(self, *args, **options):
        f = open('apps/api/csv_tables/occupations.csv', 'r')
        data = csv.reader(f)
        for index, row in enumerate(data):
            if index == 0:
                continue
            if (row[0] != ''):
                occupation= row[0]
                p, created = Occupation.objects.get_or_create(occupation=occupation)
            else:
                pass
                print ('exit')



