from django.core.management.base import BaseCommand
from finance.models import process_due_recurring


class Command(BaseCommand):
    help = "Process all due recurring transactions and create Transaction rows"

    def handle(self, *args, **options):
        created = process_due_recurring()
        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ Created {created} transaction(s) from recurring templates"))
        else:
            self.stdout.write("No due recurring transactions.")