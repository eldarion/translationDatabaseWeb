# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-19 14:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gl_tracking', '0027_partner_start_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='words',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='document',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]