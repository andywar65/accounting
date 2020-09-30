from django import forms
from django.forms import ModelForm

from .models import Invoice, CSVInvoice

class InvoiceCreateForm(ModelForm):

    def clean(self):
        cd = super().clean()
        if cd.get('active') and cd.get('category').startswith('P'):
            self.add_error('category', forms.ValidationError(
                """Stai assegnando una categoria passiva ad una fattura
                attiva!""",
                code='passive_to_active',
            ))
        elif not cd.get('active') and cd.get('category').startswith('A'):
            self.add_error('category', forms.ValidationError(
                """Stai assegnando una categoria attiva ad una fattura
                passiva!""",
                code='active_to_passive',
            ))

    class Meta:
        model = Invoice
        fields = '__all__'

class InvoiceDeleteForm(forms.Form):
    delete = forms.BooleanField( label="Cancella la fattura", required = True,
        help_text = """Attento, l'operazione non è reversibile.""")

class CSVInvoiceCreateForm(ModelForm):

    class Meta:
        model = CSVInvoice
        fields = ('csv', )
