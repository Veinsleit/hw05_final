# Generated by Django 2.2.16 on 2022-06-22 12:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_follow'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Follow',
        ),
    ]