import os

from django.conf import settings
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile

from accounting.models import Invoice, CSVInvoice

class InvoiceModelTest(TestCase):
    """Testing all methods that don't need SimpleUploadedFile"""
    @classmethod
    def setUpTestData(cls):
        invoice = Invoice.objects.create(number='001', client = 'Mr. Client',
            active = True, date = '2020-05-09', descr = 'My first invoice',
            amount = 1000, security = 10, vat = 100, category = 'A00',
            paid = False)
        csvinvoice = CSVInvoice.objects.create(date = '2020-05-09 15:53:00+02',
            csv = 'uploads/invoices/csv/sample.csv'
            )

    def test_invoice_str_method(self):
        inv = Invoice.objects.get(number='001')
        self.assertEquals(inv.__str__(), '001')

    def test_invoice_get_total_method(self):
        inv = Invoice.objects.get(number='001')
        self.assertEquals(inv.get_total(), 1110)

    def test_csvinvoice_fails_to_read_file(self):
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

@override_settings(MEDIA_ROOT=os.path.join(settings.MEDIA_ROOT, 'temp'))
class CSVInvoiceModelTest(TestCase):
    """Testing methods that need SimpleUploadedFile and CSV files"""
    @classmethod
    def setUpTestData(cls):
        csvinvoice = CSVInvoice.objects.create(date = '2020-05-01 15:53:00+02',
            csv = SimpleUploadedFile('bad_file.csv', b'Foo, Bar, FooBar, date',
            'text/csv')
            )
        content = 'Numero,Cliente,Attiva?,gg/mm/aa'
        csvinvoice2 = CSVInvoice.objects.create(date = '2020-05-02 15:53:00+02',
            csv = SimpleUploadedFile('header_file.csv', content.encode(),
            content_type="text/csv")
            )
        content = """Numero,Cliente,Attiva?,gg/mm/aa,Descrizione,Imponibile,Contributi,Iva,Categoria,Pagata?
001,Client,yes,13/04/65,Foo,1000,10,100,A00,yes"""
        csvinvoice3 = CSVInvoice.objects.create(date = '2020-05-03 15:53:00+02',
            csv = SimpleUploadedFile('created_file.csv', content.encode(),
            content_type="text/csv")
            )
        csvinvoice4 = CSVInvoice.objects.create(date = '2020-05-04 15:53:00+02',
            csv = SimpleUploadedFile('modified_file.csv', content.encode(),
            content_type="text/csv")
            )

    def tearDown(self):
        """Checks if created file exists, then removes it"""
        list = ('bad_file', 'header_file', 'created_file', 'modified_file')
        for name in list:
            if os.path.isfile(os.path.join(settings.MEDIA_ROOT,
                f'uploads/invoices/csv/{name}.csv')):
                os.remove(os.path.join(settings.MEDIA_ROOT,
                    f'uploads/invoices/csv/{name}.csv'))

    def test_csvinvoice_fails_loading_bad_file(self):
        csvinv = CSVInvoice.objects.get(date='2020-05-01 15:53:00+02')
        self.assertEquals(csvinv.created, 0)
        self.assertEquals(csvinv.modified, 0)
        self.assertEquals(csvinv.failed, 1)

    def test_csvinvoice_null_loading_header_file(self):
        csvinv = CSVInvoice.objects.get(date='2020-05-02 15:53:00+02')
        self.assertEquals(csvinv.created, 0)
        self.assertEquals(csvinv.modified, 0)
        self.assertEquals(csvinv.failed, 0)

    def test_csvinvoice_success_loading_created_file(self):
        csvinv = CSVInvoice.objects.get(date='2020-05-03 15:53:00+02')
        self.assertEquals(csvinv.created, 1)
        self.assertEquals(csvinv.modified, 0)
        self.assertEquals(csvinv.failed, 0)

    def test_csvinvoice_alert_loading_modified_file(self):
        csvinv = CSVInvoice.objects.get(date='2020-05-04 15:53:00+02')
        csvinv.save()
        self.assertEquals(csvinv.created, 0)
        self.assertEquals(csvinv.modified, 1)
        self.assertEquals(csvinv.failed, 0)

@override_settings(MEDIA_ROOT=os.path.join(settings.MEDIA_ROOT, 'temp'))
class XMLInvoiceModelTest(TestCase):
    """Testing methods that need SimpleUploadedFile and XML files"""
    @classmethod
    def setUpTestData(cls):
        xmlinvoice5 = CSVInvoice.objects.create(date = '2020-05-05 15:53:00+02',
            csv = SimpleUploadedFile('bad_file.xml', b'<Foo><Bar></Bar></Foo>',
            'text/xml')
            )
        content = """
<Fattura versione="FPR12">
    <CedentePrestatore>
        <Denominazione>Associazione Professionale Perilli</Denominazione>
    </CedentePrestatore>
    <CessionarioCommittente>
        <Denominazione>Miglior Cliente</Denominazione>
    </CessionarioCommittente>
    <Data>1965-04-13</Data>
    <Numero>001/1965</Numero>
    <ImportoContributoCassa>10</ImportoContributoCassa>
    <Descrizione>Un lavoro malfatto</Descrizione>
    <PrezzoTotale>1000</PrezzoTotale>
    <Imposta>100</Imposta>
</Fattura>"""
        xmlinvoice6 = CSVInvoice.objects.create(date = '2020-05-06 15:53:00+02',
            csv = SimpleUploadedFile('created_file.xml', content.encode(),
            'text/xml')
            )
        content = """
<Fattura versione="FPR12">
    <CedentePrestatore>
        <Nome>Miglior</Nome>
        <Cognome>Fornitura</Cognome>
    </CedentePrestatore>
    <CessionarioCommittente>
        <Denominazione>Associazione Professionale Perilli</Denominazione>
    </CessionarioCommittente>
    <Data>1967-04-23</Data>
    <Numero>001/1967</Numero>
    <Descrizione>Una fornitura indecente</Descrizione>
    <PrezzoTotale>1000</PrezzoTotale>
    <Descrizione>Un'altra fornitura indecente</Descrizione>
    <PrezzoTotale>2000</PrezzoTotale>
    <Imposta>300</Imposta>
</Fattura>"""
        xmlinvoice7 = CSVInvoice.objects.create(date = '2020-05-07 15:53:00+02',
            csv = SimpleUploadedFile('modified_file.xml', content.encode(),
            'text/xml')
            )

    def tearDown(self):
        """Checks if created file exists, then removes it"""
        list = ('bad_file', 'created_file', 'modified_file')
        for name in list:
            if os.path.isfile(os.path.join(settings.MEDIA_ROOT,
                f'uploads/invoices/csv/{name}.xml')):
                os.remove(os.path.join(settings.MEDIA_ROOT,
                    f'uploads/invoices/csv/{name}.xml'))

    def test_xmlinvoice_fails_loading_bad_file(self):
        xmlinv = CSVInvoice.objects.get(date='2020-05-05 15:53:00+02')
        self.assertEquals(xmlinv.created, 0)
        self.assertEquals(xmlinv.modified, 0)
        self.assertEquals(xmlinv.failed, 1)

    def test_xmlinvoice_success_loading_created_file(self):
        xmlinv = CSVInvoice.objects.get(date='2020-05-06 15:53:00+02')
        self.assertEquals(xmlinv.created, 1)
        self.assertEquals(xmlinv.modified, 0)
        self.assertEquals(xmlinv.failed, 0)

    def test_xmlinvoice_alert_loading_modified_file(self):
        xmlinv = CSVInvoice.objects.get(date='2020-05-07 15:53:00+02')
        xmlinv.save()
        self.assertEquals(xmlinv.created, 0)
        self.assertEquals(xmlinv.modified, 1)
        self.assertEquals(xmlinv.failed, 0)
