from django.test import TestCase

from accounting.models import Invoice, CSVInvoice

class InvoiceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        invoice = Invoice.objects.create(number='001', client = 'Mr. Client',
            active = True, date = '2020-05-09', descr = 'My first invoice',
            amount = 1000, security = 10, vat = 100, category = 'A00',
            paid = False)

    def test_invoice_str_method(self):
        inv = Invoice.objects.get(number='001')
        self.assertEquals(inv.__str__(), '001')
