# Generated by Django 2.1.13 on 2019-11-06 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0026_auto_20191106_0935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='in_memory_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='members',
            name='in_memory_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]