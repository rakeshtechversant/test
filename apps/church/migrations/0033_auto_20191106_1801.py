# Generated by Django 2.1.13 on 2019-11-06 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0032_merge_20191106_1751'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notice',
            name='primary_user_access',
        ),
        migrations.RemoveField(
            model_name='notice',
            name='secondary_user_access',
        ),
        migrations.AlterField(
            model_name='notice',
            name='notice',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]