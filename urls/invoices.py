from django.urls import path
from accounting.views import (InvoiceArchiveIndexView, InvoiceCreateView,
    InvoiceUpdateView)

app_name = 'invoices'
urlpatterns = [
    path('', InvoiceArchiveIndexView.as_view(), name = 'index'),
    path('add/', InvoiceCreateView.as_view(), name = 'add'),
    path('change/invoice/<pk>/', InvoiceUpdateView.as_view(), name = 'change'),
    ]
