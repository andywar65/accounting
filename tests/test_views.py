from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from users.models import User
from accounting.models import Invoice, CSVInvoice

class InvoiceViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        usr = User.objects.create_user(username='logged_in',
            password='P4s5W0r6')
        content_type = ContentType.objects.get_for_model(Invoice)
        permission = Permission.objects.get(
            codename='view_invoice',
            content_type=content_type,
        )
        usr.user_permissions.add(permission)
