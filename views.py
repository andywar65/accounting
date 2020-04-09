from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, FormView
from django.views.generic.dates import ( ArchiveIndexView, YearArchiveView,
    MonthArchiveView )
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Invoice
from .forms import InvoiceCreateForm, InvoiceDeleteForm
from .choices import CAT

class InvoiceArchiveIndexView(LoginRequiredMixin, ArchiveIndexView):
    model = Invoice
    date_field = 'date'
    allow_future = True
    context_object_name = 'all_invoices'
    paginate_by = 50
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'created' in self.request.GET:
            context['created'] = self.request.GET['created']
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
        context['active_sum'] = sum
        #total passive invoices
        sum = Decimal('0.00')
        for inv in passive:
            sum += inv.get_total()
        context['passive_sum'] = sum
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

class InvoiceYearArchiveView(LoginRequiredMixin, ChartMixin, YearArchiveView):
    model = Invoice
    make_object_list = True
    date_field = 'date'
    allow_future = True
    context_object_name = 'all_invoices'
    year_format = '%Y'
    allow_empty = True

class InvoiceMonthArchiveView(LoginRequiredMixin, ChartMixin, MonthArchiveView):
    model = Invoice
    date_field = 'date'
    allow_future = True
    context_object_name = 'all_invoices'
    year_format = '%Y'
    month_format = '%m'
    allow_empty = True

class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceCreateForm
    success_url = '/fatture?created=True' # reverse_lazy('invoices:index')

class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceCreateForm
    success_url = reverse_lazy('invoices:index')
    template_name = 'accounting/invoice_update_form.html'

class InvoiceDeleteView(LoginRequiredMixin, FormView):
    model = Invoice
    form_class = InvoiceDeleteForm
    success_url = reverse_lazy('invoices:index')
    template_name = 'accounting/invoice_delete_form.html'

    def form_valid(self, form):
        invoice = get_object_or_404(Invoice, id = self.kwargs['pk'])
        invoice.delete()
        return super(InvoiceDeleteView, self).form_valid(form)
