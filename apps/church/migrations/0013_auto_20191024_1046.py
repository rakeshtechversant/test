# Generated by Django 2.1.13 on 2019-10-24 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0012_auto_20191024_0914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='mobile_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
