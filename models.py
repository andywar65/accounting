from django.db import models
from django.utils.timezone import now

from filebrowser.fields import FileBrowseField

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

class CSVInvoice(models.Model):
    date = models.DateTimeField('Data', default = now, )
    csv = FileBrowseField("File CSV", max_length=200,
        extensions=[".csv", ], directory="invoices/csv/",)

    def __str__(self):
        return self.date.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        verbose_name = 'File CSV'
        verbose_name_plural = 'File CSV'
        ordering = ('-date', )
