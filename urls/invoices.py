from django.urls import path
from accounting.views import (InvoiceArchiveIndexView, InvoiceYearArchiveView,
    InvoiceMonthArchiveView, InvoiceCreateView, InvoiceUpdateView,
    InvoiceDeleteView, CSVInvoiceCreateView, year_download, month_download)

app_name = 'invoices'
urlpatterns = [
    path('', InvoiceArchiveIndexView.as_view(), name = 'index'),
    path('<int:year>/', InvoiceYearArchiveView.as_view(),
        name = 'year'),
    path('<int:year>/download/', year_download, name = 'year_download'),
    path('<int:year>/<int:month>/', InvoiceMonthArchiveView.as_view(),
        name = 'month'),
    path('<int:year>/<int:month>/download/', month_download,
        name = 'month_download'),
    path('add/', InvoiceCreateView.as_view(), name = 'add'),
    path('add/csv/', CSVInvoiceCreateView.as_view(), name = 'csv'),
    path('change/invoice/<pk>/', InvoiceUpdateView.as_view(), name = 'change'),
    path('delete/invoice/<pk>/', InvoiceDeleteView.as_view(), name = 'delete'),
    ]
