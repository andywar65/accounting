from django.contrib import admin
from .models import Invoice, CSVInvoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'client', 'active', 'date', 'get_total',
        'category', 'paid', )

@admin.register(CSVInvoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('get_filename', 'date', )
