# Generated by Django 2.1.13 on 2019-11-06 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adminprofile',
            name='mobile_number',
            field=models.CharField(default='1234567890', max_length=100),
            preserve_default=False,
        ),
    ]
