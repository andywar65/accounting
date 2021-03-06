# Generated by Django 3.1.2 on 2020-12-23 18:11

import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CSVInvoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data')),
                ('csv', models.FileField(max_length=200, upload_to='uploads/invoices/csv/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['csv', 'xml'])], verbose_name='File CSV / XML')),
                ('created', models.IntegerField(default=0, editable=False)),
                ('modified', models.IntegerField(default=0, editable=False)),
                ('failed', models.IntegerField(default=0, editable=False)),
            ],
            options={
                'verbose_name': 'File CSV/XML',
                'verbose_name_plural': 'File CSV/XML',
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=50, verbose_name='Numero')),
                ('client', models.CharField(max_length=100, verbose_name='Cliente/Fornitore')),
                ('active', models.BooleanField(default=False, help_text='Attiva se spuntata, altrimenti passiva', verbose_name='Attiva')),
                ('date', models.DateField(default=django.utils.timezone.now, verbose_name='Data')),
                ('descr', models.TextField(blank=True, null=True, verbose_name='Causale')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Imponibile')),
                ('security', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name='Contributi')),
                ('vat', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name='IVA')),
                ('category', models.CharField(choices=[('A01PR', 'A-Progettazione architettonica'), ('A02DL', 'A-Direzione lavori'), ('A03CT', 'A-Catasto'), ('A04PE', 'A-Perizie'), ('A05AN', 'A-Anticipazioni'), ('A00', 'A-Varie'), ('X', 'Altro'), ('P05CO', 'P-Collaboratori'), ('P01AU', 'P-Automobili'), ('P02AT', 'P-Attrezzature'), ('P14SE', 'P-Servizi'), ('P13FO', 'P-Formazione'), ('P03CA', 'P-Cancelleria'), ('P04TE', 'P-Telefoni'), ('P11ER', 'P-Erogazioni'), ('P12AF', 'P-Affitti'), ('P07AS', 'P-Assicurazioni'), ('P09PR', 'P-Contributi'), ('P10TA', 'P-Tasse'), ('P06RE', 'P-Restituzioni'), ('P08DI', 'P-Dividendi'), ('P00', 'P-Varie')], default='X', help_text="'A' per attiva e 'P' per passiva.\n            ", max_length=5, verbose_name='Categoria')),
                ('paid', models.BooleanField(default=False, verbose_name='Saldata')),
            ],
            options={
                'verbose_name': 'Fattura',
                'verbose_name_plural': 'Fatture',
                'ordering': ('-date',),
            },
        ),
    ]
