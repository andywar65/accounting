from decimal import Decimal
import csv
from datetime import datetime

from imap_tools import MailBox, AND

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, UpdateView, FormView, TemplateView
from django.views.generic.dates import ( ArchiveIndexView, YearArchiveView,
    MonthArchiveView, )
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.translation import gettext as _
from django.urls import reverse

from .models import Invoice, CSVInvoice
from .forms import InvoiceCreateForm, InvoiceDeleteForm, CSVInvoiceCreateForm
from .management.commands.fetch_invoice_emails import do_command
from .choices import CAT

class InvoiceArchiveIndexView(PermissionRequiredMixin, ArchiveIndexView):
    model = Invoice
    permission_required = 'accounting.view_invoice'
    date_field = 'date'
    allow_future = True
    context_object_name = 'all_invoices'
    paginate_by = 50
    allow_empty = True

    def setup(self, request, *args, **kwargs):
        super(InvoiceArchiveIndexView, self).setup(request, *args, **kwargs)
        do_command()

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
            active_cat[_('Other')] = round(left, 0)
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
            passive_cat[_('Other')] = round(left, 0)
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
            return reverse('invoices:add') + f'?created={self.object.number}'
        else:
            return reverse('invoices:index') + f'?created={self.object.number}'

class InvoiceUpdateView(PermissionRequiredMixin, AddAnotherMixin, UpdateView):
    model = Invoice
    permission_required = 'accounting.change_invoice'
    form_class = InvoiceCreateForm
    template_name = 'accounting/invoice_update_form.html'

    def get_success_url(self):
        if 'add_another' in self.request.POST:
            return reverse('invoices:add') + f'?modified={self.object.number}'
        else:
            return reverse('invoices:index') + f'?modified={self.object.number}'

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
        return reverse('invoices:index') + f'?deleted={self.number}'

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
            return (reverse('invoices:csv') +
                f'?csv_created={self.created}&csv_modified={self.modified}&csv_failed={self.failed}')
        else:
            return (reverse('invoices:index') +
                f'?csv_created={self.created}&csv_modified={self.modified}&csv_failed={self.failed}')

def csv_writer(writer, qs):
    writer.writerow([_('Number'), _('Client'), _('Active?'), _('dd/mm/yy'),
        _('Description'), _('Taxable'), _('Social security'), _('VAT'),
        _('Category'), _('Paid?')])
    for i in qs:
        active = 'yes' if i.active else ''
        paid = 'yes' if i.paid else ''
        date = datetime.strftime(i.date, '%d/%m/%y')
        writer.writerow([i.number, i.client, active, date, i.descr,
            i.amount, i.security, i.vat, i.category, paid])
    return writer

@permission_required('accounting.view_invoice')
def year_download(request, year):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = ('attachment; filename="%(invoices)s-%(year)d.csv"' %
        {'invoices': _('Invoices'), 'year': year})

    qs = Invoice.objects.filter(date__year=year)

    writer = csv.writer(response)
    writer = csv_writer(writer, qs)

    return response

@permission_required('accounting.view_invoice')
def month_download(request, year, month):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = ('attachment; filename="%(invoices)s-%(year)d-%(month)d.csv"' %
        {'invoices': _('Invoices'), 'year': year, 'month': month})

    qs = Invoice.objects.filter(date__year=year).filter(date__month=month)

    writer = csv.writer(response)
    writer = csv_writer(writer, qs)

    return response

#class CSVInvoiceMailTemplateView(PermissionRequiredMixin, TemplateView):
    #permission_required = 'accounting.view_invoice'
    #template_name = 'accounting/email.html'

    #def get_context_data(self, **kwargs):
        #context = super().get_context_data(**kwargs)

        #context['csv_created'] = 0
        #context['csv_modified'] = 0
        #context['csv_failed'] = 0

        #HOST = settings.IMAP_HOST
        #USER = settings.IMAP_USER
        #PASSWORD = settings.IMAP_PWD
        #PORT = settings.IMAP_PORT
        #FROM = settings.IMAP_FROM

        #with MailBox(HOST).login(USER, PASSWORD, 'INBOX') as mailbox:
            #for message in mailbox.fetch(AND(seen=False, subject=_('invoices'),
                #from_=FROM), mark_seen=True):
                #for att in message.attachments:  # list: [Attachment objects]
                    #file = SimpleUploadedFile(att.filename, att.payload,
                        #att.content_type)
                    #instance = CSVInvoice(csv=file)
                    #instance.save()
                    #context['csv_created'] += instance.created
                    #context['csv_modified'] += instance.modified
                    #context['csv_failed'] += instance.failed
        #return context
