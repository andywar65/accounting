from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, FormView
from django.views.generic.dates import ( ArchiveIndexView, YearArchiveView,
    MonthArchiveView )
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Invoice
from .forms import InvoiceCreateForm, InvoiceDeleteForm

class InvoiceArchiveIndexView(LoginRequiredMixin, ArchiveIndexView):
    model = Invoice
    date_field = 'date'
    allow_future = True
    context_object_name = 'all_invoices'
    paginate_by = 50
    allow_empty = True

class ChartMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active = context['all_invoices'].filter(active = True)
        passive = context['all_invoices'].filter(active = False)
        sum = 0
        for inv in active:
            sum += inv.get_total()
        context['active_sum'] = sum
        sum = 0
        for inv in passive:
            sum += inv.get_total()
        context['passive_sum'] = sum
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
    success_url = reverse_lazy('invoices:index')

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
