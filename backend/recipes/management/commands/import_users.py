from csv import DictReader

from django.core.management import BaseCommand
from users.models import User

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""


class Command(BaseCommand):
    # Show this when the user types help
    help = "Loads data from csv"

    def handle(self, *args, **options):
        # Show this when the data already exist in the database
        if User.objects.exists():
            print('category data already loaded...exiting.')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return
        # Show this before loading the data into the database
        print("Loading users data")

        # Code to load the data into database
        for row in DictReader(open('./users.csv')):
            user = User(username=row['username'], email=row['email'], first_name=row['first_name'], last_name=row['last_name'], password=row['password'])
            user.save()
