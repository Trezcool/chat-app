# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-29 14:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='friend',
            name='is_favorite',
            field=models.BooleanField(default=False),
        ),
    ]
