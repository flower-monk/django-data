# Generated by Django 4.0.5 on 2022-06-05 07:15

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('wordpad', '0003_alter_articlepost_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlepost',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 5, 7, 15, 56, 797903, tzinfo=utc)),
        ),
    ]
