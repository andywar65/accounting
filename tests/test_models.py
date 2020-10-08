import os

from django.conf import settings
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile

from accounting.models import Invoice, CSVInvoice

@override_settings(MEDIA_ROOT=os.path.join(settings.MEDIA_ROOT, 'temp'))
class InvoiceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        invoice = Invoice.objects.create(number='001', client = 'Mr. Client',
            active = True, date = '2020-05-09', descr = 'My first invoice',
            amount = 1000, security = 10, vat = 100, category = 'A00',
            paid = False)
        csvinvoice = CSVInvoice.objects.create(date = '2020-05-09 15:53:00+02',
            csv = SimpleUploadedFile('sample.csv', b'Foo, Bar'))

    def tearDown(self):
        os.remove(os.path.join(settings.MEDIA_ROOT,
            'uploads/invoices/csv/sample.csv'))

    def test_invoice_str_method(self):
        inv = Invoice.objects.get(number='001')
        self.assertEquals(inv.__str__(), '001')

    def test_invoice_get_total_method(self):
        inv = Invoice.objects.get(number='001')
        self.assertEquals(inv.get_total(), 1110)

    def test_csvinvoice_fails_reading_file(self):
        csvinv = CSVInvoice.objects.get(date='2020-05-09 15:53:00+02')
        self.assertEquals(csvinv.created, 0)
        self.assertEquals(csvinv.modified, 0)
        self.assertEquals(csvinv.failed, 1)

    def test_csvinvoice_str_method(self):
        csvinv = CSVInvoice.objects.get(date='2020-05-09 15:53:00+02')
        self.assertEquals(csvinv.__str__(), f'File - {csvinv.id}')

    def test_csvinvoice_get_filename(self):
        csvinv = CSVInvoice.objects.get(date='2020-05-09 15:53:00+02')
        self.assertEquals(csvinv.get_filename(), 'sample.csv')

    def test_csvinvoice_prepare_float(self):
        csvinv = CSVInvoice.objects.get(date='2020-05-09 15:53:00+02')
        value = '€1.000,00'
        self.assertEquals(csvinv.prepare_float(value), 1000.00)

    def test_csvinvoice_prepare_float_0(self):
        csvinv = CSVInvoice.objects.get(date='2020-05-09 15:53:00+02')
        value = ''
        self.assertEquals(csvinv.prepare_float(value), 0)

    def test_csvinvoice_guess_passive_category(self):
        csvinv = CSVInvoice.objects.get(date='2020-05-09 15:53:00+02')
        dict = {'Renault': 'P01AU', 'Telecom': 'P04TE',
            'Giordanella': 'P05CO', 'Xerox': 'P02AT',
            'Aruba': 'P14SE','Ufficio Moderno': 'P03CA',}
        for string, cat in dict.items():
            self.assertEquals(csvinv.guess_passive_category(string), cat)

    def test_csvinvoice_guess_passive_category_fail(self):
        csvinv = CSVInvoice.objects.get(date='2020-05-09 15:53:00+02')
        string = 'Citroen'
        self.assertEquals(csvinv.guess_passive_category(string), 'P00')

    def test_csvinvoice_guess_active_category(self):
        csvinv = CSVInvoice.objects.get(date='2020-05-09 15:53:00+02')
        dict = {'Progetto': 'A01PR', 'DL': 'A02DL',
            'Catasto': 'A03CT', 'Perizia': 'A04PE',}
        for string, cat in dict.items():
            self.assertEquals(csvinv.guess_active_category(string), cat)

    def test_csvinvoice_guess_active_category_fail(self):
        csvinv = CSVInvoice.objects.get(date='2020-05-09 15:53:00+02')
        string = 'pulizia cessi'
        self.assertEquals(csvinv.guess_active_category(string), 'A00')
