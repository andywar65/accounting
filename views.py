from django.shortcuts import render
from django.views.generic.dates import ArchiveIndexView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Invoice

class InvoiceArchiveIndexView(LoginRequiredMixin, ArchiveIndexView):
    model = Invoice
    date_field = 'date'
    allow_future = True
    context_object_name = 'all_invoices'
    paginate_by = 50
    allow_empty = True
