# Generated by Django 2.1.13 on 2019-11-05 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0011_noticebereavement'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileupload',
            name='about',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='fileupload',
            name='marital_status',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='fileupload',
            name='occupation',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='members',
            name='about',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='members',
            name='blood_group',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='members',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='members',
            name='marital_status',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='members',
            name='occupation',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='members',
            name='phone_no_secondary_user_secondary',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
