# Generated by Django 2.2.2 on 2019-10-02 18:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bear_applications', '0003_auto_20191002_1822'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='version',
            name='architecture',
        ),
        migrations.RemoveField(
            model_name='version',
            name='toolchain',
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('architecture', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bear_applications.Architecture')),
                ('toolchain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bear_applications.Toolchain')),
                ('version', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bear_applications.Version')),
            ],
            options={
                'unique_together': {('version', 'toolchain', 'architecture')},
            },
        ),
    ]
