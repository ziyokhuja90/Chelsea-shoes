# Generated by Django 5.1.3 on 2025-05-27 12:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_references_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='producement',
            name='producement_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='home.producement'),
        ),
    ]
