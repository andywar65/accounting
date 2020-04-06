from django.urls import path
from accounting.views import (InvoiceArchiveIndexView, InvoiceYearArchiveView,
    InvoiceMonthArchiveView, InvoiceCreateView, InvoiceUpdateView,
    InvoiceDeleteView)

app_name = 'invoices'
urlpatterns = [
    path('', InvoiceArchiveIndexView.as_view(), name = 'index'),
    path('<int:year>/', InvoiceYearArchiveView.as_view(),
        name = 'year'),
    path('<int:year>/<int:month>/', InvoiceMonthArchiveView.as_view(),
        name = 'month'),
    path('add/', InvoiceCreateView.as_view(), name = 'add'),
    path('change/invoice/<pk>/', InvoiceUpdateView.as_view(), name = 'change'),
    path('delete/invoice/<pk>/', InvoiceDeleteView.as_view(), name = 'delete'),
    ]
