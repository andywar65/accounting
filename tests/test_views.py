import os
from decimal import Decimal

from django.conf import settings
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
        adder = User.objects.create_user(username='adder',
            password='P4s5W0r6')
        content_type = ContentType.objects.get_for_model(Invoice)
        permission = Permission.objects.get(
            codename='view_invoice',
            content_type=content_type,
        )
        viewer.user_permissions.add(permission)
        content_type_2 = ContentType.objects.get_for_model(CSVInvoice)
        permissions = (Permission.objects.filter(content_type__in=[content_type,
            content_type_2]))
        adder.user_permissions.set(permissions)
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

    def test_invoice_month_view_status_code_not_logged(self):
        response = self.client.get(reverse('invoices:month',
            kwargs={'year': '2020', 'month': '05'}))
        self.assertEqual(response.status_code, 302)

    def test_invoice_month_view_status_code_logged(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:month',
            kwargs={'year': '2020', 'month': '05'}))
        self.assertEqual(response.status_code, 200)

    def test_invoice_month_view_template_logged(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:month',
            kwargs={'year': '2020', 'month': '05'}))
        self.assertTemplateUsed(response,
            'accounting/invoice_archive_month.html')

    def test_invoice_month_view_context(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        all_invoices = Invoice.objects.filter(date__year=2020)
        all_invoices = all_invoices.filter(date__month=5)
        response = self.client.get(reverse('invoices:month',
            kwargs={'year': '2020', 'month': '05'}))
        self.assertQuerysetEqual(response.context['all_invoices'], all_invoices,
            transform=lambda x: x)

    def test_invoice_create_view_status_code_no_perm(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:add'))
        self.assertEqual(response.status_code, 403)

    def test_invoice_create_view_template_no_perm(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:add'))
        self.assertTemplateUsed(response, '403.html')

    def test_invoice_create_view_status_code_perm(self):
        self.client.post('/accounts/login/', {'username':'adder',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:add'))
        self.assertEqual(response.status_code, 200)

    def test_invoice_create_view_template_perm(self):
        self.client.post('/accounts/login/', {'username':'adder',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:add'))
        self.assertTemplateUsed(response, 'accounting/invoice_form.html')

    def test_invoice_create_view_post_validation_active(self):
        """We test form validation and response code. Category 0 code means
        the code of the first category error (can be more than one)"""
        self.client.post('/accounts/login/', {'username':'adder',
            'password':'P4s5W0r6'})
        response = self.client.post('/fatture/add/', {'number': '999',
            'client': 'Mr. Bean', 'active': True, 'date': '09/10/20',
            'amount': 1000, 'security': 10, 'vat': 100, 'category': 'P01AU',
            'paid': False})
        self.assertEqual(response.context['form'].errors.as_data()['category'][0].code,
            'passive_to_active')
        self.assertEqual(response.status_code, 200)

    def test_invoice_create_view_post_validation_passive(self):
        self.client.post('/accounts/login/', {'username':'adder',
            'password':'P4s5W0r6'})
        response = self.client.post('/fatture/add/', {'number': '999',
            'client': 'Mr. Bean', 'active': False, 'date': '09/10/20',
            'amount': 1000, 'security': 10, 'vat': 100, 'category': 'A01PR',
            'paid': False})
        self.assertEqual(response.context['form'].errors.as_data()['category'][0].code,
            'active_to_passive')
        self.assertEqual(response.status_code, 200)#error, so no redirect

    def test_invoice_create_view_post_success_redirect(self):
        self.client.post('/accounts/login/', {'username':'adder',
            'password':'P4s5W0r6'})
        response = self.client.post('/fatture/add/', {'number': '999',
            'client': 'Mr. Bean', 'active': True, 'date': '09/10/20',
            'amount': 1000, 'security': 10, 'vat': 100, 'category': 'A01PR',
            'paid': False}, follow = True)#remember to follow
        self.assertRedirects(response, '/fatture/?created=999', status_code = 302,
            target_status_code = 200)#302 is first step of redirect chain

    def test_invoice_create_view_post_success_redirect_add_another(self):
        self.client.post('/accounts/login/', {'username':'adder',
            'password':'P4s5W0r6'})
        #add_another True is the button that saves and adds another invoice
        response = self.client.post('/fatture/add/', {'number': '998',
            'client': 'Mr. Bean', 'active': True, 'date': '09/10/20',
            'amount': 1000, 'security': 10, 'vat': 100, 'category': 'A01PR',
            'paid': False, 'add_another': True }, follow = True)
        self.assertRedirects(response, '/fatture/add/?created=998',
            status_code = 302, target_status_code = 200)

    def test_invoice_update_view_status_code_no_perm(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.get(f'/fatture/change/invoice/{inv.id}/')
        self.assertEqual(response.status_code, 403)

    def test_invoice_update_view_template_no_perm(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.get(f'/fatture/change/invoice/{inv.id}/')
        self.assertTemplateUsed(response, '403.html')

    def test_invoice_update_view_status_code_perm(self):
        self.client.post('/accounts/login/', {'username':'adder',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.get(f'/fatture/change/invoice/{inv.id}/')
        self.assertEqual(response.status_code, 200)

    def test_invoice_update_view_template_perm(self):
        self.client.post('/accounts/login/', {'username':'adder',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.get(f'/fatture/change/invoice/{inv.id}/')
        self.assertTemplateUsed(response, 'accounting/invoice_update_form.html')

    def test_invoice_update_view_post_success_redirect(self):
        self.client.post('/accounts/login/', {'username':'adder',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.post(f'/fatture/change/invoice/{inv.id}/',
            {'number': '002', 'client': 'Mr. Bean', 'active': True,
            'date': '09/10/20', 'amount': 1000, 'security': 10, 'vat': 100,
            'category': 'A01PR', 'paid': False}, follow = True)
        self.assertRedirects(response, '/fatture/?modified=002', status_code=302,
            target_status_code = 200)#302 is first step of redirect chain

    def test_invoice_update_view_post_success_redirect_add_another(self):
        self.client.post('/accounts/login/', {'username':'adder',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        #add_another True is the button that saves and adds another invoice
        response = self.client.post(f'/fatture/change/invoice/{inv.id}/',
            {'number': '002', 'client': 'Mr. Bean', 'active': True,
            'date': '09/10/20', 'amount': 1000, 'security': 10, 'vat': 100,
            'category': 'A01PR', 'paid': False, 'add_another': True },
            follow = True)
        self.assertRedirects(response, '/fatture/add/?modified=002',
            status_code = 302, target_status_code = 200)

    def test_invoice_delete_view_status_code_no_perm(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.get(f'/fatture/delete/invoice/{inv.id}/')
        self.assertEqual(response.status_code, 403)

    def test_invoice_delete_view_template_no_perm(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.get(f'/fatture/delete/invoice/{inv.id}/')
        self.assertTemplateUsed(response, '403.html')

    def test_invoice_delete_view_status_code_perm(self):
        self.client.post('/accounts/login/', {'username':'adder',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.get(f'/fatture/delete/invoice/{inv.id}/')
        self.assertEqual(response.status_code, 200)

    def test_invoice_delete_view_template_perm(self):
        self.client.post('/accounts/login/', {'username':'adder',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.get(f'/fatture/delete/invoice/{inv.id}/')
        self.assertTemplateUsed(response, 'accounting/invoice_delete_form.html')

    def test_invoice_delete_view_post_success_redirect(self):
        self.client.post('/accounts/login/', {'username':'adder',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.post(f'/fatture/delete/invoice/{inv.id}/',
            {'delete': True, }, follow = True)
        self.assertRedirects(response, '/fatture/?deleted=002', status_code=302,
            target_status_code = 200)#302 is first step of redirect chain

    def test_csvinvoice_add_view_status_code_no_perm(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:csv'))
        self.assertEqual(response.status_code, 403)

    def test_csvinvoice_add_view_template_no_perm(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:csv'))
        self.assertTemplateUsed(response, '403.html')

    def test_csvinvoice_add_view_status_code_perm(self):
        self.client.post('/accounts/login/', {'username':'adder',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:csv'))
        self.assertEqual(response.status_code, 200)

    def test_csvinvoice_add_view_template_perm(self):
        self.client.post('/accounts/login/', {'username':'adder',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:csv'))
        self.assertTemplateUsed(response, 'accounting/csvinvoice_form.html')

    def test_csvinvoice_add_view_post_success_redirect(self):
        self.client.post('/accounts/login/', {'username':'adder',
            'password':'P4s5W0r6'})
        file_path = os.path.join(settings.BASE_DIR,
            'accounting/static/accounting/sample.csv')
        with open(file_path) as csv_file:
            response = self.client.post('/fatture/add/csv/',
                {'csv': csv_file,
                'date': '2020-05-09 15:53:00+02'}, follow = True)
        csv_file.close()
        self.assertRedirects(response,
            '/fatture/?csv_created=2&csv_modified=0&csv_failed=0',
            status_code=302, target_status_code = 200)

    def test_csvinvoice_add_view_post_success_redirect_add_another(self):
        self.client.post('/accounts/login/', {'username':'adder',
            'password':'P4s5W0r6'})
        #add_another True is the button that saves and adds another invoice
        file_path = os.path.join(settings.BASE_DIR,
            'accounting/static/accounting/sample.csv')
        with open(file_path) as csv_file:
            response = self.client.post('/fatture/add/csv/',
                {'csv': csv_file,
                'date': '2020-05-10 15:53:00+02', 'add_another': True},
                follow = True)
        csv_file.close()
        self.assertRedirects(response,
            '/fatture/add/csv/?csv_created=2&csv_modified=0&csv_failed=0',
            status_code = 302, target_status_code = 200)

    def test_year_download_view_redirects_no_log(self):
        response = self.client.get(reverse('invoices:year_download',
            kwargs={'year': '2020'}), follow = True)
        self.assertRedirects(response,
            '/accounts/login/?next=%2Ffatture%2F2020%2Fdownload%2F',
            status_code=302, target_status_code = 200)

    def test_year_download_view_status_code_perm(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:year_download',
            kwargs={'year': '2020'}), follow = True)
        self.assertEqual(response.status_code, 200)

    def test_month_download_view_redirects_no_log(self):
        response = self.client.get(reverse('invoices:month_download',
            kwargs={'year': '2020', 'month': '05'}), follow = True)
        self.assertRedirects(response,
            '/accounts/login/?next=%2Ffatture%2F2020%2F05%2Fdownload%2F',
            status_code=302, target_status_code = 200)

    def test_month_download_view_status_code_perm(self):
        self.client.post('/accounts/login/', {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:month_download',
            kwargs={'year': '2020', 'month': '05'}), follow = True)
        self.assertEqual(response.status_code, 200)
