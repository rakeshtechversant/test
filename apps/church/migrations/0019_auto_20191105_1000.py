# Generated by Django 2.1.13 on 2019-11-05 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0018_merge_20191105_0944'),
    ]

    operations = [
        migrations.AddField(
            model_name='churchdetails',
            name='vicar_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='churchdetails',
            name='vicar_image',
            field=models.FileField(blank=True, null=True, upload_to='pan_folder/'),
        ),
    ]