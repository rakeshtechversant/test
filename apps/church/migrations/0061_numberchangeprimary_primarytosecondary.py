# Generated by Django 2.1.13 on 2020-01-10 08:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0060_auto_20191219_1714'),
    ]

    operations = [
        migrations.CreateModel(
            name='NumberChangePrimary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_from_primary', models.CharField(blank=True, max_length=200, null=True)),
                ('number_from', models.CharField(blank=True, max_length=12, null=True)),
                ('number_to', models.CharField(blank=True, max_length=12, null=True)),
                ('is_accepted', models.BooleanField(default=False)),
                ('date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
            ],
        ),
        migrations.CreateModel(
            name='PrimaryToSecondary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_from', models.CharField(blank=True, max_length=200, null=True)),
                ('usertype_from', models.CharField(blank=True, max_length=200, null=True)),
                ('request_to', models.CharField(blank=True, max_length=200, null=True)),
                ('is_accepted', models.BooleanField(default=False)),
                ('date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
            ],
        ),
    ]