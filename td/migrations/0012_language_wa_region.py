# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-28 15:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('td', '0011_waregion'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='wa_region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='td.WARegion'),
        ),
    ]
