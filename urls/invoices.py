from django.urls import path
from django.utils.translation import gettext_lazy as _

from accounting.views import (InvoiceArchiveIndexView, InvoiceYearArchiveView,
    InvoiceMonthArchiveView, InvoiceCreateView, InvoiceUpdateView,
    InvoiceDeleteView, CSVInvoiceCreateView, year_download, month_download,
    CSVInvoiceMailTemplateView)

app_name = 'invoices'
urlpatterns = [
    path('', InvoiceArchiveIndexView.as_view(), name = 'index'),
    path('<int:year>/', InvoiceYearArchiveView.as_view(),
        name = 'year'),
    path(_('<int:year>/download/'), year_download, name = 'year_download'),
    path('<int:year>/<int:month>/', InvoiceMonthArchiveView.as_view(),
        name = 'month'),
    path(_('<int:year>/<int:month>/download/'), month_download,
        name = 'month_download'),
    path(_('add/'), InvoiceCreateView.as_view(), name = 'add'),
    path(_('add/csv/'), CSVInvoiceCreateView.as_view(), name = 'csv'),
    path(_('change/<pk>/'), InvoiceUpdateView.as_view(),
        name = 'change'),
    path(_('delete/<pk>/'), InvoiceDeleteView.as_view(),
        name = 'delete'),
    #path('email/', CSVInvoiceMailTemplateView.as_view(), name = 'email'),
    ]
