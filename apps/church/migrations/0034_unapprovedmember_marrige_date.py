# Generated by Django 2.1.13 on 2019-11-06 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0033_auto_20191106_1801'),
    ]

    operations = [
        migrations.AddField(
            model_name='unapprovedmember',
            name='marrige_date',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
