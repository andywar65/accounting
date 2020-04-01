# Generated by Django 3.0.4 on 2020-04-01 22:33

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=50, verbose_name='Numero')),
                ('client', models.CharField(max_length=100, verbose_name='Cliente/Fornitore')),
                ('active', models.BooleanField(default=False, verbose_name='Attiva/Passiva')),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data')),
                ('descr', models.TextField(blank=True, null=True, verbose_name='Causale')),
                ('amount', models.FloatField(verbose_name='Imponibile')),
                ('security', models.FloatField(blank=True, null=True, verbose_name='Contributo previdenziale')),
                ('vat', models.FloatField(blank=True, null=True, verbose_name='IVA')),
                ('category', models.CharField(choices=[('A01PR', 'A-Progettazione'), ('A02DL', 'A-Direzione lavori'), ('A03CT', 'A-Catasto'), ('X', 'Altro')], default='X', help_text="'A' per le attive e 'P' per le passive.\n            ", max_length=5, verbose_name='Categoria')),
                ('paid', models.BooleanField(default=False, verbose_name='Pagata')),
            ],
            options={
                'verbose_name': 'Fattura',
                'verbose_name_plural': 'Fatture',
                'ordering': ('-date',),
            },
        ),
    ]
