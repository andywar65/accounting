# Generated by Django 3.1.2 on 2020-10-25 21:23

import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    replaces = [('accounting', '0001_initial'), ('accounting', '0002_auto_20200404_1835'), ('accounting', '0003_auto_20200405_2346'), ('accounting', '0004_auto_20200927_2257'), ('accounting', '0005_auto_20200928_0026'), ('accounting', '0006_auto_20201001_2346'), ('accounting', '0007_auto_20201003_1749'), ('accounting', '0008_auto_20201006_1556'), ('accounting', '0009_auto_20201006_1602'), ('accounting', '0010_csvinvoice_failed')]

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
                ('active', models.BooleanField(default=False, help_text='Se selezionato è attiva, altrimenti è passiva', verbose_name='Attiva')),
                ('date', models.DateField(default=django.utils.timezone.now, verbose_name='Data')),
                ('descr', models.TextField(blank=True, null=True, verbose_name='Causale')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Imponibile')),
                ('security', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name='Contributo previdenziale')),
                ('vat', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name='IVA')),
                ('category', models.CharField(choices=[('A01PR', 'A-Progettazione'), ('A02DL', 'A-Direzione lavori'), ('A03CT', 'A-Catasto'), ('A04PE', 'A-Perizie'), ('A05AN', 'A-Anticipazioni'), ('A00', 'A-Varie'), ('X', 'Altro'), ('P05CO', 'P-Collaboratori'), ('P01AU', 'P-Autoveicoli'), ('P02AT', 'P-Attrezzature'), ('P14SE', 'P-Servizi'), ('P13FO', 'P-Formazione'), ('P03CA', 'P-Cancelleria'), ('P04TE', 'P-Telefoni'), ('P11ER', 'P-Erogazioni'), ('P12AF', 'P-Affitti'), ('P07AS', 'P-Assicurazioni'), ('P09PR', 'P-Previdenza'), ('P10TA', 'P-Tasse'), ('P06RE', 'P-Restituzioni'), ('P08DI', 'P-Dividendi'), ('P00', 'P-Varie')], default='X', help_text="'A' per le attive e 'P' per le passive.\n            ", max_length=5, verbose_name='Categoria')),
                ('paid', models.BooleanField(default=False, verbose_name='Pagata')),
            ],
            options={
                'verbose_name': 'Fattura',
                'verbose_name_plural': 'Fatture',
                'ordering': ('-date',),
            },
        ),
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
    ]