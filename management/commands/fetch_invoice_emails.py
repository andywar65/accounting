from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.translation import gettext as _

from imap_tools import MailBox, AND

from accounting.models import CSVInvoice
from users.models import User

def do_command():

    if not settings.FETCH_EMAILS:
        return

    HOST = settings.IMAP_HOST
    USER = settings.IMAP_USER
    PASSWORD = settings.IMAP_PWD
    PORT = settings.IMAP_PORT
    FROM = settings.IMAP_FROM

    with MailBox(HOST).login(USER, PASSWORD, 'INBOX') as mailbox:
        for message in mailbox.fetch(AND(seen=False, subject=_('invoices'), ),
            mark_seen=True):
            try:
                usr = User.objects.get(email=message.from_)
                if not usr.has_perm('accounting.add_csvinvoice'):
                    continue
            except:
                continue
            for att in message.attachments:  # list: [Attachment objects]
                file = SimpleUploadedFile(att.filename, att.payload,
                    att.content_type)
                instance = CSVInvoice(csv=file)
                instance.save()

class Command(BaseCommand):

    def handle(self, *args, **options):
        do_command()
