from django.urls import path
from accounting.views import *

app_name = 'invoices'
urlpatterns = [
    path('', InvoiceArchiveIndexView.as_view(), name = 'index'),
    ]
