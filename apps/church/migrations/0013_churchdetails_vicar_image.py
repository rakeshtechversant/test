# Generated by Django 2.1.13 on 2019-11-05 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0012_auto_20191105_0452'),
    ]

    operations = [
        migrations.AddField(
            model_name='churchdetails',
            name='vicar_image',
            field=models.ImageField(blank=True, null=True, upload_to='pan_folder/'),
        ),
    ]