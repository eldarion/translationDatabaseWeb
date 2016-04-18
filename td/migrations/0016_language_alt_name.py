# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-04 20:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('td', '0015_language_add_alt_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='alt_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='td.LanguageAltName'),
        ),
    ]