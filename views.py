from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, FormView
from django.views.generic.dates import ( ArchiveIndexView, YearArchiveView,
    MonthArchiveView )
from django.contrib.auth.mixins import PermissionRequiredMixin

from .models import Invoice, CSVInvoice
from .forms import InvoiceCreateForm, InvoiceDeleteForm, CSVInvoiceCreateForm
from .choices import CAT

class InvoiceArchiveIndexView(PermissionRequiredMixin, ArchiveIndexView):
    model = Invoice
    permission_required = 'accounting.view_invoice'
    date_field = 'date'
    allow_future = True
    context_object_name = 'all_invoices'
    paginate_by = 50
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'created' in self.request.GET:
            context['created'] = self.request.GET['created']
        elif 'modified' in self.request.GET:
            context['modified'] = self.request.GET['modified']
        elif 'deleted' in self.request.GET:
            context['deleted'] = self.request.GET['deleted']
        elif 'csv_created' in self.request.GET:
            context['csv_created'] = self.request.GET['csv_created']
            context['csv_modified'] = self.request.GET['csv_modified']
        return context

class ChartMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active = context['all_invoices'].filter(active = True)
        passive = context['all_invoices'].filter(active = False)
        choices = CAT
        #total active invoices
        sum = Decimal('0.00')
        for inv in active:
            sum += inv.get_total()
        context['active_sum'] = round(sum, 0)
        #total passive invoices
        sum = Decimal('0.00')
        for inv in passive:
            sum += inv.get_total()
        context['passive_sum'] = round(sum, 0)
        #total active invoices by category
        active_cat = {}
        active_left = Decimal('0.00')
        for ch in choices:
            if ch[0].startswith('A'):
                act_cat = active.filter(category = ch[0])
                sum = Decimal('0.00')
                for act in act_cat:
                    sum += act.get_total()
                active_cat[ch[1].replace('A-', '')] = round(sum, 0)
                active_left += sum
            left = context['active_sum'] - active_left
            active_cat['Altro'] = round(left, 0)
        context['active_cat'] = active_cat
        #total active invoices by category
        passive_cat = {}
        passive_left = Decimal('0.00')
        for ch in choices:
            if ch[0].startswith('P'):
                pass_cat = passive.filter(category = ch[0])
                sum = Decimal('0.00')
                for pasv in pass_cat:
                    sum += pasv.get_total()
                passive_cat[ch[1].replace('P-', '')] = round(sum, 0)
                passive_left += sum
            left = context['passive_sum'] - passive_left
            passive_cat['Altro'] = round(left, 0)
        context['passive_cat'] = passive_cat
        return context

class InvoiceYearArchiveView(PermissionRequiredMixin, ChartMixin, YearArchiveView):
    model = Invoice
    permission_required = 'accounting.view_invoice'
    make_object_list = True
    date_field = 'date'
    allow_future = True
    context_object_name = 'all_invoices'
    year_format = '%Y'
    allow_empty = True

class InvoiceMonthArchiveView(PermissionRequiredMixin, ChartMixin, MonthArchiveView):
    model = Invoice
    permission_required = 'accounting.view_invoice'
    date_field = 'date'
    allow_future = True
    context_object_name = 'all_invoices'
    year_format = '%Y'
    month_format = '%m'
    allow_empty = True

class AddAnotherMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'created' in self.request.GET:
            context['created'] = self.request.GET['created']
        elif 'modified' in self.request.GET:
            context['modified'] = self.request.GET['modified']
        return context

class InvoiceCreateView(PermissionRequiredMixin, AddAnotherMixin, CreateView):
    model = Invoice
    permission_required = 'accounting.add_invoice'
    form_class = InvoiceCreateForm

    def get_success_url(self):
        if 'add_another' in self.request.POST:
            return f'/fatture/add?created={self.object.number}'
        else:
            return f'/fatture?created={self.object.number}'

class InvoiceUpdateView(PermissionRequiredMixin, AddAnotherMixin, UpdateView):
    model = Invoice
    permission_required = 'accounting.change_invoice'
    form_class = InvoiceCreateForm
    template_name = 'accounting/invoice_update_form.html'

    def get_success_url(self):
        if 'add_another' in self.request.POST:
            return f'/fatture/add?modified={self.object.number}'
        else:
            return f'/fatture?modified={self.object.number}'

class InvoiceDeleteView(PermissionRequiredMixin, FormView):
    model = Invoice
    permission_required = 'accounting.delete_invoice'
    form_class = InvoiceDeleteForm
    template_name = 'accounting/invoice_delete_form.html'

    def form_valid(self, form):
        invoice = get_object_or_404(Invoice, id = self.kwargs['pk'])
        self.number = invoice.number
        invoice.delete()
        return super(InvoiceDeleteView, self).form_valid(form)

    def get_success_url(self):
        return f'/fatture?deleted={self.number}'

class CSVInvoiceCreateView(PermissionRequiredMixin, CreateView):
    model = CSVInvoice
    permission_required = 'accounting.add_csvinvoice'
    form_class = CSVInvoiceCreateForm

    def get_success_url(self):
        return f'/fatture?csv_created={self.object.created}&csv_modified={self.object.modified}'
