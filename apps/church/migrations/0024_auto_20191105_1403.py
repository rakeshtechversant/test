# Generated by Django 2.1.13 on 2019-11-05 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0023_auto_20191105_1218'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='familyimage/'),
        ),
        migrations.AlterField(
            model_name='fileupload',
            name='occupation',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]