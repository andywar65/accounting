# Generated by Django 3.1.2 on 2020-10-06 14:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0008_auto_20201006_1556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Data'),
        ),
    ]
