from decimal import Decimal
import csv

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, FormView
from django.views.generic.dates import ( ArchiveIndexView, YearArchiveView,
    MonthArchiveView )
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required

from .models import Invoice, CSVInvoice
from .forms import InvoiceCreateForm, InvoiceDeleteForm, CSVInvoiceCreateForm
from .choices import CAT

@permission_required('accounting.view_invoice')
def year_download(request, year):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    writer = csv.writer(response)
    writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
    writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])

    return response

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
            context['csv_failed'] = self.request.GET['csv_failed']
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
        elif 'csv_created' in self.request.GET:
            context['csv_created'] = self.request.GET['csv_created']
            context['csv_modified'] = self.request.GET['csv_modified']
            context['csv_failed'] = self.request.GET['csv_failed']
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

class CSVInvoiceCreateView(PermissionRequiredMixin, AddAnotherMixin, FormView):
    model = CSVInvoice
    template_name = 'accounting/csvinvoice_form.html'
    permission_required = 'accounting.add_csvinvoice'
    form_class = CSVInvoiceCreateForm

    def form_valid(self, form):
        self.created = 0
        self.modified = 0
        self.failed = 0
        files = self.request.FILES.getlist('csv')
        for f in files:
            instance = CSVInvoice(csv=f)
            instance.save()
            self.created += instance.created
            self.modified += instance.modified
            self.failed += instance.failed
        return super(CSVInvoiceCreateView, self).form_valid(form)

    def get_success_url(self):
        if 'add_another' in self.request.POST:
            return f'/fatture/add/csv?csv_created={self.created}&csv_modified={self.modified}&csv_failed={self.failed}'
        else:
            return f'/fatture?csv_created={self.created}&csv_modified={self.modified}&csv_failed={self.failed}'
