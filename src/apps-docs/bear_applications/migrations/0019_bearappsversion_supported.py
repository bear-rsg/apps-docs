# Generated by Django 3.0.9 on 2020-12-09 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bear_applications', '0018_architecture_displayed_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='bearappsversion',
            name='supported',
            field=models.BooleanField(default=True),
        ),
    ]