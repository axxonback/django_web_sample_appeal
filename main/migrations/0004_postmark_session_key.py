# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-18 11:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20160418_0910'),
    ]

    operations = [
        migrations.AddField(
            model_name='postmark',
            name='session_key',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
    ]
