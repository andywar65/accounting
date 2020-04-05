from django import forms
from django.forms import ModelForm

from .models import Invoice

class InvoiceCreateForm(ModelForm):

    class Meta:
        model = Invoice
        fields = '__all__'

class InvoiceDeleteForm(forms.Form):
    delete = forms.BooleanField( label="Cancella la fattura", required = True,
        help_text = """Attento, l'operazione non è reversibile.""")
