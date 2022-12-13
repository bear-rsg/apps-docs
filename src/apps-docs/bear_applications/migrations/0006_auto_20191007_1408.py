# Generated by Django 2.2.2 on 2019-10-07 14:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bear_applications', '0005_auto_20191003_0844'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Toolchain',
            new_name='BearAppsVersion',
        ),
        migrations.RenameField(
            model_name='link',
            old_name='toolchain',
            new_name='bearappsversion',
        ),
        migrations.AlterUniqueTogether(
            name='link',
            unique_together={('version', 'bearappsversion', 'architecture')},
        ),
    ]
