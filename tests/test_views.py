import os
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext as _

from users.models import User
from accounting.models import Invoice, CSVInvoice

class InvoiceViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        noviewer = User.objects.create_user(username='noviewer',
            password='P4s5W0r6')
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
        group = Group.objects.get(name='Accounting')
        adder.groups.add(group)
        content_type_2 = ContentType.objects.get_for_model(CSVInvoice)
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
        self.assertRedirects(response, reverse('front_login')+'?next='+reverse('invoices:index'))

    def test_invoice_archive_view_status_code_logged(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:index'))
        self.assertEqual(response.status_code, 200)

    def test_invoice_archive_view_template_logged(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:index'))
        self.assertTemplateUsed(response, 'accounting/invoice_archive.html')

    def test_invoice_archive_view_context(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        all_invoices = Invoice.objects.all()
        response = self.client.get(reverse('invoices:index'))
        self.assertQuerysetEqual(response.context['all_invoices'], all_invoices,
            transform=lambda x: x)

    def test_invoice_archive_view_context_alternatives(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:index')+'?created=001')
        self.assertEqual(response.context['created'], '001')
        response = self.client.get(reverse('invoices:index')+'?modified=001')
        self.assertEqual(response.context['modified'], '001')
        response = self.client.get(reverse('invoices:index')+'?deleted=001')
        self.assertEqual(response.context['deleted'], '001')
        response = self.client.get(reverse('invoices:index')+'?csv_created=99&csv_modified=18&csv_failed=1')
        self.assertEqual(response.context['csv_created'], '99')
        self.assertEqual(response.context['csv_modified'], '18')
        self.assertEqual(response.context['csv_failed'], '1')

    def test_invoice_year_view_status_code_not_logged(self):
        response = self.client.get(reverse('invoices:year',
            kwargs={'year': '2020'}))
        self.assertEqual(response.status_code, 302)

    def test_invoice_year_view_status_code_logged(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:year',
            kwargs={'year': '2020'}))
        self.assertEqual(response.status_code, 200)

    def test_invoice_year_view_template_logged(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:year',
            kwargs={'year': '2020'}))
        self.assertTemplateUsed(response, 'accounting/invoice_archive_year.html')

    def test_invoice_year_view_context(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        all_invoices = Invoice.objects.filter(date__year=2020)
        response = self.client.get(reverse('invoices:year',
            kwargs={'year': '2020'}))
        self.assertQuerysetEqual(response.context['all_invoices'], all_invoices,
            transform=lambda x: x)

    def test_invoice_year_view_sum_context(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:year',
            kwargs={'year': '2020'}))
        self.assertEqual(response.context['active_sum'], 1110)
        self.assertEqual(response.context['passive_sum'], 2220)
        #WARNING next may fail if new categories are added to choices
        self.assertEqual(response.context['active_cat'], {
            _('Other'): Decimal('0'),
            _('Advance payment'): Decimal('0'),
            _('Land registry'): Decimal('0'),
            _('Construction supervision'): Decimal('0'),
            _('Expertise'): Decimal('0'),
            _('Architectural design'): Decimal('1110'),
            _('Various'): Decimal('0')})
        self.assertEqual(response.context['passive_cat'], {
            _('Rentals'): Decimal('0'),
            _('Other'): Decimal('0'),
            _('Assurances'): Decimal('0'),
            _('Equipment'): Decimal('0'),
            _('Fleet'): Decimal('2220'),
            _('Office products'): Decimal('0'),
            _('Staff'): Decimal('0'),
            _('Dividends'): Decimal('0'),
            _('Supplies'): Decimal('0'),
            _('Training'): Decimal('0'),
            _('Social security'): Decimal('0'),
            _('Refunds'): Decimal('0'),
            _('Services'): Decimal('0'),
            _('Taxes'): Decimal('0'),
            _('Telecom'): Decimal('0'),
            _('Various'): Decimal('0')})

    def test_invoice_month_view_status_code_not_logged(self):
        response = self.client.get(reverse('invoices:month',
            kwargs={'year': '2020', 'month': '05'}))
        self.assertEqual(response.status_code, 302)

    def test_invoice_month_view_status_code_logged(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:month',
            kwargs={'year': '2020', 'month': '05'}))
        self.assertEqual(response.status_code, 200)

    def test_invoice_month_view_template_logged(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:month',
            kwargs={'year': '2020', 'month': '05'}))
        self.assertTemplateUsed(response,
            'accounting/invoice_archive_month.html')

    def test_invoice_month_view_context(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        all_invoices = Invoice.objects.filter(date__year=2020)
        all_invoices = all_invoices.filter(date__month=5)
        response = self.client.get(reverse('invoices:month',
            kwargs={'year': '2020', 'month': '05'}))
        self.assertQuerysetEqual(response.context['all_invoices'], all_invoices,
            transform=lambda x: x)

    def test_invoice_create_view_status_code_no_perm(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:add'))
        self.assertEqual(response.status_code, 403)

    def test_invoice_create_view_template_no_perm(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:add'))
        self.assertTemplateUsed(response, '403.html')

    def test_invoice_create_view_status_code_perm(self):
        self.client.post(reverse('front_login'), {'username':'adder',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:add'))
        self.assertEqual(response.status_code, 200)

    def test_invoice_create_view_template_perm(self):
        self.client.post(reverse('front_login'), {'username':'adder',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:add'))
        self.assertTemplateUsed(response, 'accounting/invoice_form.html')

    def test_invoice_create_view_post_validation_active(self):
        """We test form validation and response code. Category 0 code means
        the code of the first category error (can be more than one)"""
        self.client.post(reverse('front_login'), {'username':'adder',
            'password':'P4s5W0r6'})
        response = self.client.post(reverse('invoices:add'), {'number': '999',
            'client': 'Mr. Bean', 'active': True, 'date': '09/10/20',
            'amount': 1000, 'security': 10, 'vat': 100, 'category': 'P01AU',
            'paid': False})
        self.assertEqual(response.context['form'].errors.as_data()['category'][0].code,
            'passive_to_active')
        self.assertEqual(response.status_code, 200)

    def test_invoice_create_view_post_validation_passive(self):
        self.client.post(reverse('front_login'), {'username':'adder',
            'password':'P4s5W0r6'})
        response = self.client.post(reverse('invoices:add'), {'number': '999',
            'client': 'Mr. Bean', 'active': False, 'date': '09/10/20',
            'amount': 1000, 'security': 10, 'vat': 100, 'category': 'A01PR',
            'paid': False})
        self.assertEqual(response.context['form'].errors.as_data()['category'][0].code,
            'active_to_passive')
        self.assertEqual(response.status_code, 200)#error, so no redirect

    def test_invoice_create_view_post_success_redirect(self):
        self.client.post(reverse('front_login'), {'username':'adder',
            'password':'P4s5W0r6'})
        response = self.client.post(reverse('invoices:add'), {'number': '999',
            'client': 'Mr. Bean', 'active': True, 'date': '09/10/20',
            'amount': 1000, 'security': 10, 'vat': 100, 'category': 'A01PR',
            'paid': False}, follow = True)#remember to follow
        self.assertRedirects(response, reverse('invoices:index')+'?created=999',
            status_code = 302,
            target_status_code = 200)#302 is first step of redirect chain

    def test_invoice_create_view_post_success_redirect_add_another(self):
        self.client.post(reverse('front_login'), {'username':'adder',
            'password':'P4s5W0r6'})
        #add_another True is the button that saves and adds another invoice
        response = self.client.post(reverse('invoices:add'), {'number': '998',
            'client': 'Mr. Bean', 'active': True, 'date': '09/10/20',
            'amount': 1000, 'security': 10, 'vat': 100, 'category': 'A01PR',
            'paid': False, 'add_another': True }, follow = True)
        self.assertRedirects(response, reverse('invoices:add')+'?created=998',
            status_code = 302, target_status_code = 200)

    def test_invoice_update_view_status_code_no_perm(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.get(reverse('invoices:change',
            kwargs={ 'pk': inv.id }))
        self.assertEqual(response.status_code, 403)

    def test_invoice_update_view_template_no_perm(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.get(reverse('invoices:change',
            kwargs={ 'pk': inv.id }))
        self.assertTemplateUsed(response, '403.html')

    def test_invoice_update_view_status_code_perm(self):
        self.client.post(reverse('front_login'), {'username':'adder',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.get(reverse('invoices:change',
            kwargs={ 'pk': inv.id }))
        self.assertEqual(response.status_code, 200)

    def test_invoice_update_view_template_perm(self):
        self.client.post(reverse('front_login'), {'username':'adder',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.get(reverse('invoices:change',
            kwargs={ 'pk': inv.id }))
        self.assertTemplateUsed(response, 'accounting/invoice_update_form.html')

    def test_invoice_update_view_post_success_redirect(self):
        self.client.post(reverse('front_login'), {'username':'adder',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.post(reverse('invoices:change',
            kwargs={ 'pk': inv.id }),
            {'number': '002', 'client': 'Mr. Bean', 'active': True,
            'date': '09/10/20', 'amount': 1000, 'security': 10, 'vat': 100,
            'category': 'A01PR', 'paid': False}, follow = True)
        self.assertRedirects(response,
            reverse('invoices:index')+'?modified=002', status_code=302,
            target_status_code = 200)#302 is first step of redirect chain

    def test_invoice_update_view_post_success_redirect_add_another(self):
        self.client.post(reverse('front_login'), {'username':'adder',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        #add_another True is the button that saves and adds another invoice
        response = self.client.post(reverse('invoices:change',
            kwargs={ 'pk': inv.id }),
            {'number': '002', 'client': 'Mr. Bean', 'active': True,
            'date': '09/10/20', 'amount': 1000, 'security': 10, 'vat': 100,
            'category': 'A01PR', 'paid': False, 'add_another': True },
            follow = True)
        self.assertRedirects(response, reverse('invoices:add')+'?modified=002',
            status_code = 302, target_status_code = 200)

    def test_invoice_delete_view_status_code_no_perm(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.get(reverse('invoices:delete',
            kwargs={ 'pk': inv.id }))
        self.assertEqual(response.status_code, 403)

    def test_invoice_delete_view_template_no_perm(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.get(reverse('invoices:delete',
            kwargs={ 'pk': inv.id }))
        self.assertTemplateUsed(response, '403.html')

    def test_invoice_delete_view_status_code_perm(self):
        self.client.post(reverse('front_login'), {'username':'adder',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.get(reverse('invoices:delete',
            kwargs={ 'pk': inv.id }))
        self.assertEqual(response.status_code, 200)

    def test_invoice_delete_view_template_perm(self):
        self.client.post(reverse('front_login'), {'username':'adder',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.get(reverse('invoices:delete',
            kwargs={ 'pk': inv.id }))
        self.assertTemplateUsed(response, 'accounting/invoice_delete_form.html')

    def test_invoice_delete_view_post_success_redirect(self):
        self.client.post(reverse('front_login'), {'username':'adder',
            'password':'P4s5W0r6'})
        inv = Invoice.objects.get(number='002')
        response = self.client.post(reverse('invoices:delete',
            kwargs={ 'pk': inv.id }),
            {'delete': True, }, follow = True)
        self.assertRedirects(response, reverse('invoices:index')+'?deleted=002',
            status_code=302,
            target_status_code = 200)#302 is first step of redirect chain

    def test_csvinvoice_add_view_status_code_no_perm(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:csv'))
        self.assertEqual(response.status_code, 403)

    def test_csvinvoice_add_view_template_no_perm(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:csv'))
        self.assertTemplateUsed(response, '403.html')

    def test_csvinvoice_add_view_status_code_perm(self):
        self.client.post(reverse('front_login'), {'username':'adder',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:csv'))
        self.assertEqual(response.status_code, 200)

    def test_csvinvoice_add_view_template_perm(self):
        self.client.post(reverse('front_login'), {'username':'adder',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:csv'))
        self.assertTemplateUsed(response, 'accounting/csvinvoice_form.html')

    def test_csvinvoice_add_view_post_success_redirect(self):
        self.client.post(reverse('front_login'), {'username':'adder',
            'password':'P4s5W0r6'})
        file_path = os.path.join(settings.BASE_DIR,
            'accounting/static/accounting/sample.csv')
        with open(file_path) as csv_file:
            response = self.client.post(reverse('invoices:csv'),
                {'csv': csv_file,
                'date': '2020-05-09 15:53:00+02'}, follow = True)
        csv_file.close()
        self.assertRedirects(response,
            reverse('invoices:index')+'?csv_created=2&csv_modified=0&csv_failed=0',
            status_code=302, target_status_code = 200)

    def test_csvinvoice_add_view_post_success_redirect_add_another(self):
        self.client.post(reverse('front_login'), {'username':'adder',
            'password':'P4s5W0r6'})
        #add_another True is the button that saves and adds another invoice
        file_path = os.path.join(settings.BASE_DIR,
            'accounting/static/accounting/sample.csv')
        with open(file_path) as csv_file:
            response = self.client.post(reverse('invoices:csv'),
                {'csv': csv_file,
                'date': '2020-05-10 15:53:00+02', 'add_another': True},
                follow = True)
        csv_file.close()
        self.assertRedirects(response,
            reverse('invoices:csv')+'?csv_created=2&csv_modified=0&csv_failed=0',
            status_code = 302, target_status_code = 200)

    def test_year_download_view_redirects_no_log(self):
        response = self.client.get(reverse('invoices:year_download',
            kwargs={'year': '2020'}), follow = True)
        self.assertRedirects(response,
            reverse('front_login')+'?next='+reverse('invoices:year_download',
            kwargs={ 'year': '2020' } ),
            status_code=302, target_status_code = 200)

    def test_year_download_view_status_code_perm(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:year_download',
            kwargs={'year': '2020'}), follow = True)
        self.assertEqual(response.status_code, 200)

    def test_month_download_view_redirects_no_log(self):
        response = self.client.get(reverse('invoices:month_download',
            kwargs={'year': '2020', 'month': '05'}), follow = True)
        self.assertRedirects(response,
            reverse('front_login')+'?next='+reverse('invoices:month_download',
            kwargs={'year': '2020', 'month': '05'} ),
            status_code=302, target_status_code = 200)

    def test_month_download_view_status_code_perm(self):
        self.client.post(reverse('front_login'), {'username':'viewer',
            'password':'P4s5W0r6'})
        response = self.client.get(reverse('invoices:month_download',
            kwargs={'year': '2020', 'month': '05'}), follow = True)
        self.assertEqual(response.status_code, 200)

    #def test_csvinvoice_email_view_redirects_no_log(self):
        #response = self.client.get(reverse('invoices:email'))
        #self.assertRedirects(response,
            #'/accounts/login/?next=%2Ffatture%2Femail%2F',
            #status_code=302, target_status_code = 200)

    #def test_csvinvoice_email_view_status_code_no_perm(self):
        #self.client.post('/accounts/login/', {'username':'noviewer',
            #'password':'P4s5W0r6'})
        #response = self.client.get(reverse('invoices:email'))
        #self.assertEqual(response.status_code, 403)

    #def test_csvinvoice_email_view_status_code_perm(self):
        #self.client.post('/accounts/login/', {'username':'viewer',
            #'password':'P4s5W0r6'})
        #response = self.client.get(reverse('invoices:email'))
        #self.assertEqual(response.status_code, 200)

    #def test_csvinvoice_email_view_context_perm(self):
        #"""Of course no mail is fetched, so counters stay at 0"""
        #self.client.post('/accounts/login/', {'username':'viewer',
            #'password':'P4s5W0r6'})
        #response = self.client.get(reverse('invoices:email'))
        #self.assertEqual(response.context['csv_created'], 0)
        #self.assertEqual(response.context['csv_modified'], 0)
        #self.assertEqual(response.context['csv_failed'], 0)
