# Generated by Django 2.1.13 on 2019-11-20 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0055_noticebereavement_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='images',
            name='title',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
    ]
