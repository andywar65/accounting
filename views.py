from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.views.generic.dates import ArchiveIndexView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Invoice
from .forms import InvoiceCreateForm

class InvoiceArchiveIndexView(LoginRequiredMixin, ArchiveIndexView):
    model = Invoice
    date_field = 'date'
    allow_future = True
    context_object_name = 'all_invoices'
    paginate_by = 50
    allow_empty = True

class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceCreateForm
    success_url = reverse_lazy('invoices:index')

class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceCreateForm
    success_url = reverse_lazy('invoices:index')
    template_name = 'accounting/invoice_update_form.html'
