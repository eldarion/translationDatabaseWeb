# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-25 16:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('td', '0009_auto_20160113_2045'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='region',
            name='wa_director',
        ),
    ]