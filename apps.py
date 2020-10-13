from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_accounting_group(sender, **kwargs):
    from django.contrib.auth.models import Permission, Group
    grp, created = Group.objects.get_or_create(name='Accounting')
    if created:
        permission = Permission.objects.filter(codename__in=("view_invoice",
            'add_invoice', 'change_invoice', 'delete_invoice', 'view_csvinvoice',
            'add_csvinvoice', 'change_csvinvoice', 'delete_csvinvoice'))
        grp.permissions.set(permission)

class AccountingConfig(AppConfig):
    name = 'accounting'

    def ready(self):
        post_migrate.connect(create_accounting_group, sender=self)
