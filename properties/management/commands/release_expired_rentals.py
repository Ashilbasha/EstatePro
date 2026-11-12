from django.core.management.base import BaseCommand
from django.utils import timezone
from properties.models import Booking, Property


class Command(BaseCommand):
    help = "Release completed rental properties whose rental end date has passed."

    def handle(self, *args, **options):
        today = timezone.localdate()
        expired = Booking.objects.filter(
            booking_type='rent',
            status='completed',
            rental_end_date__lt=today,
            property__status='rented',
        ).select_related('property')

        released = 0
        for booking in expired:
            prop = booking.property
            # Do not release if another completed rental is still active.
            active = Booking.objects.filter(
                property=prop,
                booking_type='rent',
                status='completed',
                rental_end_date__gte=today,
            ).exists()
            if not active:
                prop.status = 'available'
                prop.save(update_fields=['status', 'updated_at'])
                released += 1

        self.stdout.write(self.style.SUCCESS(f"Released {released} expired rental properties."))
