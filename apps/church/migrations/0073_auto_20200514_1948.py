# Generated by Django 2.1.13 on 2020-05-14 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0072_changerequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changerequest',
            name='mobile_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='changerequest',
            name='user_name',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
