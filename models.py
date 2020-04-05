from django.db import models
from django.utils.timezone import now
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
