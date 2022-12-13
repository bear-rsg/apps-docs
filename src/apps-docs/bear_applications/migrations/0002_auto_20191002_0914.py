# Generated by Django 2.2.2 on 2019-10-02 09:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bear_applications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='paragraphdata',
            name='application',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bear_applications.Application'),
        ),
        migrations.AlterField(
            model_name='paragraphdata',
            name='version',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bear_applications.Version'),
        ),
    ]
