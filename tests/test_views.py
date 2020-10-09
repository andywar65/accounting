from decimal import Decimal

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from users.models import User
from accounting.models import Invoice, CSVInvoice

class InvoiceViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        viewer = User.objects.create_user(username='viewer',
            password='P4s5W0r6')
        content_type = ContentType.objects.get_for_model(Invoice)
        permission = Permission.objects.get(
            codename='view_invoice',
            content_type=content_type,
        )
        viewer.user_permissions.add(permission)
        invoice2 = Invoice.objects.create(number='002', client = 'Mr. Client',
            active = True, date = '2020-05-02', descr = 'My first invoice',
            amount = 1000, security = 10, vat = 100, category = 'A01PR',
            paid = False)
        invoice3 = Invoice.objects.create(number='003', client = 'Mr. Client',
            active = False, date = '2020-06-03', descr = 'My first invoice',
            amount = 2000, security = 20, vat = 200, category = 'P01AU',
            paid = False)
        invoice4 = Invoice.objects.create(number='004', client = 'Mr. Client',
            active = False, date = '2019-06-03', descr = 'My first invoice',
            amount = 1000, security = 10, vat = 100, category = 'P02AT',
            paid = False)

    def test_invoice_archive_view_status_code_not_logged(self):
        response = self.client.get(reverse('invoices:index'))
        self.assertEqual(response.status_code, 302)

    def test_invoice_archive_view_redirects_not_logged(self):
        response = self.client.get(reverse('invoices:index'))
        self.assertRedirects(response, '/accounts/login/?next=%2Ffatture%2F')

    def test_invoice_archive_view_status_code_logged(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:index'))
        self.assertEqual(response.status_code, 200)

    def test_invoice_archive_view_template_logged(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:index'))
        self.assertTemplateUsed(response, 'accounting/invoice_archive.html')

    def test_invoice_archive_view_context(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        all_invoices = Invoice.objects.all()
        response = self.client.get(reverse('invoices:index'))
        self.assertQuerysetEqual(response.context['all_invoices'], all_invoices,
            transform=lambda x: x)

    def test_invoice_archive_view_context_alternatives(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get('/fatture/?created=001')
        self.assertEqual(response.context['created'], '001')
        response = self.client.get('/fatture/?modified=001')
        self.assertEqual(response.context['modified'], '001')
        response = self.client.get('/fatture/?deleted=001')
        self.assertEqual(response.context['deleted'], '001')
        response = self.client.get('/fatture/?csv_created=99&csv_modified=18&csv_failed=1')
        self.assertEqual(response.context['csv_created'], '99')
        self.assertEqual(response.context['csv_modified'], '18')
        self.assertEqual(response.context['csv_failed'], '1')

    def test_invoice_year_view_status_code_not_logged(self):
        response = self.client.get(reverse('invoices:year',
            kwargs={'year': '2020'}))
        self.assertEqual(response.status_code, 302)

    def test_invoice_year_view_status_code_logged(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:year',
            kwargs={'year': '2020'}))
        self.assertEqual(response.status_code, 200)

    def test_invoice_year_view_template_logged(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:year',
            kwargs={'year': '2020'}))
        self.assertTemplateUsed(response, 'accounting/invoice_archive_year.html')

    def test_invoice_year_view_context(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        all_invoices = Invoice.objects.filter(date__year=2020)
        response = self.client.get(reverse('invoices:year',
            kwargs={'year': '2020'}))
        self.assertQuerysetEqual(response.context['all_invoices'], all_invoices,
            transform=lambda x: x)

    def test_invoice_year_view_sum_context(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:year',
            kwargs={'year': '2020'}))
        self.assertEqual(response.context['active_sum'], 1110)
        self.assertEqual(response.context['passive_sum'], 2220)
        #WARNING next may fail if new categories are added to choices
        self.assertEqual(response.context['active_cat'], {
            'Altro': Decimal('0'),
            'Anticipazioni': Decimal('0'),
            'Catasto': Decimal('0'),
            'Direzione lavori': Decimal('0'),
            'Perizie': Decimal('0'),
            'Progettazione': Decimal('1110'),
            'Varie': Decimal('0')})
        self.assertEqual(response.context['passive_cat'], {
            'Affitti': Decimal('0'),
            'Altro': Decimal('0'),
            'Assicurazioni': Decimal('0'),
            'Attrezzature': Decimal('0'),
            'Autoveicoli': Decimal('2220'),
            'Cancelleria': Decimal('0'),
            'Collaboratori': Decimal('0'),
            'Dividendi': Decimal('0'),
            'Erogazioni': Decimal('0'),
            'Formazione': Decimal('0'),
            'Previdenza': Decimal('0'),
            'Restituzioni': Decimal('0'),
            'Servizi': Decimal('0'),
            'Tasse': Decimal('0'),
            'Telefoni': Decimal('0'),
            'Varie': Decimal('0')})
