# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-23 19:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('awards', '0043_summarytransactionfedacctview'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subaward',
            name='fiscal_year',
        ),
        migrations.RemoveField(
            model_name='subaward',
            name='uri',
        ),
        migrations.AddField(
            model_name='award',
            name='fiscal_year',
            field=models.IntegerField(blank=True, help_text='Fiscal Year calculated based on Action Date', null=True),
        ),
    ]
