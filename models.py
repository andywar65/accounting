import csv
import os
from datetime import datetime, date
import xml.etree.ElementTree as ET

from django.db import models
from django.utils.timezone import now
from django.core.validators import FileExtensionValidator

from .choices import CAT

class Invoice(models.Model):
    number = models.CharField('Numero', max_length = 50, )
    client = models.CharField('Cliente/Fornitore', max_length = 100, )
    active = models.BooleanField('Attiva', default=False,
        help_text = """Se selezionato è attiva, altrimenti è passiva""")
    date = models.DateField('Data', default = now, )
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
    csv = models.FileField("File CSV / XML", max_length=200,
        upload_to="uploads/invoices/csv/",
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'xml'])])
    created = models.IntegerField(default=0, editable=False)
    modified = models.IntegerField(default=0, editable=False)
    failed = models.IntegerField(default=0, editable=False)

    def prepare_float(self, value):
        if value:
            value = value.replace("€", "")
            value = value.replace(",", ".")
            value = value.replace(".", "", value.count(".") -1)
        else:
            value = '0'
        return float(value)

    def parse_csv(self):
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
                                'amount': self.prepare_float(row[5]),
                                'security': self.prepare_float(row[6]),
                                'vat': self.prepare_float(row[7]),
                                'category': row[8],
                                'paid': bool(row[9])
                                }
                            )
                        if created:
                            self.created += 1
                        else:
                            self.modified += 1
                    except: #single row fails
                        if not row[3] == 'gg/mm/aa':#means it's not header
                            self.failed += 1
        except: #all document fails
            self.created = 0
            self.modified = 0
            self.failed = 1
        super(CSVInvoice, self).save(update_fields=['created', 'modified',
            'failed'])

    def guess_passive_category(self, string):
        low = string.lower()
        auto = ['renault', 'dacia', 'telepass', 'q8', 'autostrade', 'kuwait', 'auto']
        tel = ['fastweb', 'telecom', 'wind']
        coll = ['braghetta', 'petocchi', 'giordanella']
        attr = ['xerox', 'adrastea', 'grenke']
        serv = ['progesoft', 'geoweb', 'istedil', 'aruba', 'unisapiens']
        cart = ['ufficio moderno']
        if any(x in low for x in auto):
            return 'P01AU'
        elif any(x in low for x in tel):
            return 'P04TE'
        elif any(x in low for x in coll):
            return 'P05CO'
        elif any(x in low for x in attr):
            return 'P02AT'
        elif any(x in low for x in serv):
            return 'P14SE'
        elif any(x in low for x in cart):
            return 'P03CA'
        return 'P00'

    def guess_active_category(self, string):
        low = string.lower()
        prog = ['progetto', 'progettazione', 'fattibilità']
        dl = ['dl', 'direzione lavori', 'collaudo']
        cat = ['catasto', 'catastale']
        per = ['perizia', 'relazione', 'consulenza']
        if any(x in low for x in prog):
            return 'A01PR'
        elif any(x in low for x in dl):
            return 'A02DL'
        elif any(x in low for x in cat):
            return 'A03CT'
        elif any(x in low for x in per):
            return 'A04PE'
        return 'A00'

    def parse_xml(self):
        tree = ET.parse(self.csv.path)
        root = tree.getroot()
        cp = root.find('.//CedentePrestatore')
        den = cp.find('.//Denominazione')
        if ET.iselement(den) and den.text == 'Associazione Professionale Perilli':
            active = True
            cc = root.find('.//CessionarioCommittente')
            if ET.iselement(cc.find('.//Denominazione')):
                client = cc.find('.//Denominazione').text
            else:
                client = (cc.find('.//Nome').text + ' ' +
                    cc.find('.//Cognome').text)
        else:
            active = False
            if ET.iselement(den):
                client = den.text
            else:
                client = (cp.find('.//Nome').text + ' ' +
                    cp.find('.//Cognome').text)
            category = self.guess_passive_category(client)
        date = root.find('.//Data').text
        number = root.find('.//Numero').text
        security = 0
        for sec in root.findall('.//ImportoContributoCassa'):
            security += float(sec.text)
        descr = ''
        for dsc in root.findall('.//Descrizione'):
            descr += dsc.text + '\n'
        if active:
            category = self.guess_active_category(descr)
        amount = 0
        for amnt in root.findall('.//PrezzoTotale'):
            amount += float(amnt.text)
        vat = root.find('.//Imposta').text
        #this exception catches input anomalies
        try:
            obj, created = Invoice.objects.update_or_create(
                number = number,
                date = datetime.strptime(date, '%Y-%m-%d'),
                defaults = {
                    'client': client,
                    'active': active,
                    'descr': descr,
                    'amount': amount,
                    'security': security,
                    'vat': float(vat),
                    'category': category,
                    'paid': False
                    }
                )
            if created:
                self.created += 1
            else:
                self.modified += 1
        except:
            self.failed += 1
        super(CSVInvoice, self).save(update_fields=['created', 'modified',
            'failed'])

    def save(self, *args, **kwargs):
        self.created = 0
        self.modified = 0
        self.failed = 0
        super(CSVInvoice, self).save(*args, **kwargs)
        ext = self.get_filename().split('.')[1].lower()
        if ext == 'csv':
            self.parse_csv()
        elif ext == 'xml':
            self.parse_xml()

    def get_filename(self):
        return os.path.basename(self.csv.name)
    get_filename.short_description = 'Nome file'

    def __str__(self):
        return 'File - %s' % (self.id)

    class Meta:
        verbose_name = 'File CSV/XML'
        verbose_name_plural = 'File CSV/XML'
        ordering = ('-date', )
