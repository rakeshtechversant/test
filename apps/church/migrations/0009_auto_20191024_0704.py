# Generated by Django 2.1.13 on 2019-10-24 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0008_auto_20191024_0703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='mobile_number',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
