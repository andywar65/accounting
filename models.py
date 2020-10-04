import csv
import os
from datetime import datetime

from django.db import models
from django.utils.timezone import now
from django.core.validators import FileExtensionValidator

from .choices import CAT

class Invoice(models.Model):
    number = models.CharField('Numero', max_length = 50, )
    client = models.CharField('Cliente/Fornitore', max_length = 100, )
    active = models.BooleanField('Attiva', default=False,
        help_text = """Se selezionato è attiva, altrimenti è passiva""")
    date = models.DateTimeField('Data', default = now, )
    descr = models.TextField('Causale', null=True, blank=True, )
    amount = models.DecimalField('Imponibile', max_digits=8, decimal_places=2)
    security = models.DecimalField('Contributo previdenziale', default = 0.00,
        max_digits=8, decimal_places=2 )
    vat = models.DecimalField('IVA', default = 0.00, max_digits=8,
        decimal_places=2 )
    category = models.CharField('Categoria', max_length = 5, choices = CAT,
        default = 'X', help_text = """'A' per le attive e 'P' per le passive.
            """)
    paid = models.BooleanField('Pagata', default=False, )

    def __str__(self):
        return self.number

    def get_total(self):
        return self.amount + self.security + self.vat
    get_total.short_description = 'Importo'

    class Meta:
        verbose_name = 'Fattura'
        verbose_name_plural = 'Fatture'
        ordering = ('-date', )

def prepare_float(value):
    if value:
        value = value.replace("€", "")
        value = value.replace(",", ".")
        value = value.replace(".", "", value.count(".") -1)
    else:
        value = '0'
    return float(value)

class CSVInvoice(models.Model):
    date = models.DateTimeField('Data', default = now, )
    csv = models.FileField("File CSV / XML", max_length=200,
        upload_to="uploads/invoices/csv/",
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'xml'])])
    created = models.IntegerField(default=0)
    modified = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.created = 0
        self.modified = 0
        super(CSVInvoice, self).save(*args, **kwargs)
        #this exception catches file anomalies
        try:
            with open(self.csv.path, newline='', encoding='latin-1') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    #this exception catches input anomalies
                    try:
                        obj, created = Invoice.objects.update_or_create(
                            number = row[0],
                            date = datetime.strptime(row[3], '%d/%m/%y'),
                            defaults = {
                                'client': row[1],
                                'active': bool(row[2]),
                                'descr': row[4],
                                'amount': prepare_float(row[5]),
                                'security': prepare_float(row[6]),
                                'vat': prepare_float(row[7]),
                                'category': row[8],
                                'paid': bool(row[9])
                                }
                            )
                        if created:
                            self.created += 1
                        else:
                            self.modified += 1
                    except:
                        pass
        except:
            pass
        #second save to pass created and modified
        super(CSVInvoice, self).save(update_fields=['created', 'modified'])

    def get_filename(self):
        return os.path.basename(self.csv.name)
    get_filename.short_description = 'Nome file'

    def __str__(self):
        return 'File CSV - %s' % (self.id)

    class Meta:
        verbose_name = 'File CSV'
        verbose_name_plural = 'File CSV'
        ordering = ('-date', )
