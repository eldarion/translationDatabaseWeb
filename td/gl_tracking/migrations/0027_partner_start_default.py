# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-10 16:26
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gl_tracking', '0026_update_partner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='partner_start',
            field=models.DateField(blank=True, default=datetime.date(1900, 1, 1)),
        ),
    ]
