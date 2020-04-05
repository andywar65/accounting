from django import forms
from django.forms import ModelForm

from .models import Invoice

class InvoiceCreateForm(ModelForm):

    class Meta:
        model = Invoice
        fields = '__all__'
