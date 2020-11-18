from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext as _

from .models import Invoice, CSVInvoice

class InvoiceCreateForm(ModelForm):

    def clean(self):
        cd = super().clean()
        if cd.get('active') and cd.get('category').startswith('P'):
            self.add_error('category', forms.ValidationError(
                _("""You are assigning a passive category to an active
                    invoice!"""),
                code='passive_to_active',
            ))
        elif not cd.get('active') and cd.get('category').startswith('A'):
            self.add_error('category', forms.ValidationError(
                _("""You are assigning a passive category to an active
                    invoice!"""),
                code='active_to_passive',
            ))

    class Meta:
        model = Invoice
        fields = '__all__'

class InvoiceDeleteForm(forms.Form):
    delete = forms.BooleanField( label=_("Delete the invoice"), required = True,
        help_text = _("""Caution, can't undo this."""))

class CSVInvoiceCreateForm(ModelForm):
    csv = forms.FileField(label = 'CSV / XML file',
        widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = CSVInvoice
        fields = ('csv', )
