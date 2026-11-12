# Generated for EstatePro booking enhancements.
import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('properties', '0005_property_listing_purpose_booking'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    def populate_rental_end_dates(apps, schema_editor):
        from datetime import date
        import calendar
        Booking = apps.get_model('properties', 'Booking')
        for booking in Booking.objects.all():
            booking.reference = uuid.uuid4()
            if booking.booking_type == 'rent' and booking.rental_duration_months:
                start = booking.preferred_date
                months = booking.rental_duration_months
                index = start.month - 1 + months
                year = start.year + index // 12
                month = index % 12 + 1
                day = min(start.day, calendar.monthrange(year, month)[1])
                booking.rental_end_date = date(year, month, day)
                booking.save(update_fields=['reference', 'rental_end_date'])
            else:
                booking.save(update_fields=['reference'])

    operations = [
        migrations.AddField(
            model_name='booking',
            name='reference',
            field=models.UUIDField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='rental_end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RunPython(populate_rental_end_dates, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='booking',
            name='reference',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='properties.booking')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='estate_notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='BookingStatusHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_status', models.CharField(blank=True, max_length=15)),
                ('new_status', models.CharField(max_length=15)),
                ('note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_history', to='properties.booking')),
                ('changed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
