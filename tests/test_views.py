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
