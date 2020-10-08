from django.test import TestCase

from accounting.models import Invoice, CSVInvoice

class InvoiceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        invoice = Invoice.objects.create(number='001', client = 'Mr. Client',
            active = True, date = '2020-05-09', descr = 'My first invoice',
            amount = 1000, security = 10, vat = 100, category = 'A00',
            paid = False)
        csvinvoice = CSVInvoice.objects.create(date = '2020-05-09 15:53:00+02',
            csv = 'accounting/sample.csv')

    def test_invoice_str_method(self):
        inv = Invoice.objects.get(number='001')
        self.assertEquals(inv.__str__(), '001')

    def test_invoice_get_total_method(self):
        inv = Invoice.objects.get(number='001')
        self.assertEquals(inv.get_total(), 1110)

    def test_csvinvoice_str_method(self):
        csvinv = CSVInvoice.objects.get(date='2020-05-09 15:53:00+02')
        self.assertEquals(csvinv.__str__(), f'File - {csvinv.id}')

    def test_csvinvoice_get_filename(self):
        csvinv = CSVInvoice.objects.get(date='2020-05-09 15:53:00+02')
        self.assertEquals(csvinv.get_filename(), 'sample.csv')
