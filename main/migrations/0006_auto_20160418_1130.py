# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-18 11:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20160418_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postmark',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='marks', to='main.Post'),
        ),
    ]
