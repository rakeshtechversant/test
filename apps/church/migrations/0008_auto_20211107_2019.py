# Generated by Django 2.1.13 on 2021-11-07 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0007_auto_20211107_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='name',
            field=models.CharField(max_length=20, unique=True, verbose_name='Membership_id'),
        ),
    ]
