# Generated by Django 2.2.12 on 2020-04-20 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bear_applications', '0014_auto_20200211_1653'),
    ]

    operations = [
        migrations.AddField(
            model_name='architecture',
            name='hidden',
            field=models.BooleanField(default=False),
        ),
    ]
