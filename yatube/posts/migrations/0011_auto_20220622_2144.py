# Generated by Django 2.2.16 on 2022-06-22 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_follow'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_followers'),
        ),
    ]