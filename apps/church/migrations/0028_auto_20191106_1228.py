# Generated by Django 2.1.13 on 2019-11-06 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0027_auto_20191106_0948'),
    ]

    operations = [
        migrations.AddField(
            model_name='notice',
            name='primary_user_access',
            field=models.ManyToManyField(to='church.FileUpload'),
        ),
        migrations.AddField(
            model_name='notice',
            name='secondary_user_access',
            field=models.ManyToManyField(to='church.Members'),
        ),
    ]