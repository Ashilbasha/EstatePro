import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.management import call_command

from accounts.signals import create_user_profile, save_user_profile

# Temporarily disconnect automatic profile creation
post_save.disconnect(create_user_profile, sender=User)
post_save.disconnect(save_user_profile, sender=User)

print("Profile signals temporarily disabled.")

# Import original SQLite data into MySQL
call_command('loaddata', 'estatepro_backup.json')

print("EstatePro data imported successfully!")