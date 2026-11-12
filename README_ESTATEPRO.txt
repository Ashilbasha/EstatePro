ESTATEPRO - UPDATED PROJECT
===========================

1. Extract this ZIP.
2. Open the RealEstateProject folder in VS Code.
3. Create and activate a virtual environment:
   python -m venv venv
   venv\Scripts\activate
4. Install packages:
   pip install -r requirements.txt
5. Create your local environment file:
   copy .env.example .env
   Open .env and enter a NEW Django secret key and your Gmail app password.
   Do not share the .env file.
6. Apply the new database migration:
   venv\\Scripts\\python.exe manage.py migrate
7. Check the project:
   venv\\Scripts\\python.exe manage.py check
8. Start the server:
   venv\\Scripts\\python.exe manage.py runserver

IMPORTANT DATABASE NOTE
-----------------------
The ZIP includes your uploaded db.sqlite3 and media/property_images so your existing
users, properties, inquiries and booking record are retained. Back up db.sqlite3
before running migrations.

BOOKING FEATURES ADDED
----------------------
- Unique UUID booking reference (short reference displayed in the interface).
- Rental end date calculated from requested start date and rental duration.
- Persistent customer/owner in-app notifications.
- Best-effort email notifications using the configured SMTP account.
- Booking status history and booking detail page.
- Owner can approve/reject pending requests and mark approved requests completed.
- Completing a sale marks the property Sold; completing a rental marks it Rented.
- Approval checks for conflicting approved bookings, including overlapping rental dates.
- Customer and owner booking summaries added to the dashboard.
- Property listing purpose is displayed in add/edit forms and property details.
- Admin screens for bookings, notifications and status history.

RENTAL AVAILABILITY AUTOMATION
------------------------------
Completed rentals are released back to Available after their rental end date by
running this command:
   venv\\Scripts\\python.exe manage.py release_expired_rentals

For automatic daily processing on Windows, create a Windows Task Scheduler task
that runs this command once per day, with the EstatePro project folder as the
"Start in" directory and the virtual-environment Python executable as the program:
   venv\Scripts\python.exe
Arguments:
   manage.py release_expired_rentals

NOTES
-----
- Existing Property.price is retained for backward compatibility and is still the
  single displayed price for both listing purposes. Separate sale and monthly rent
  prices have not been introduced.
- Email notifications are best-effort; in-app notifications remain available if
  SMTP is not configured.
- DEBUG remains enabled for local development. Do not deploy this configuration
  publicly without production security settings.
