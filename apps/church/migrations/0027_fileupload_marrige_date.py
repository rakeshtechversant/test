# Generated by Django 2.1.13 on 2019-11-06 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0026_auto_20191106_0749'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileupload',
            name='marrige_date',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]