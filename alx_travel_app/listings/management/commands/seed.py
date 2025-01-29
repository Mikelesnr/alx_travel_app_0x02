from django.core.management.base import BaseCommand
from alx_travel_app.listings.models import Listing,Booking,Review

class Command(BaseCommand):
    help = 'Seed the database with sample listings, bookings, and reviews'

    def handle(self, *args, **kwargs):
        # Create sample listings
        listing1 = Listing.objects.create(
            title='Sample Listing 1',
            description='This is a sample listing 1',
            price=100.00
        )
        listing2 = Listing.objects.create(
            title='Sample Listing 2',
            description='This is a sample listing 2',
            price=200.00
        )

        # Create sample bookings
        Booking.objects.create(
            listing=listing1,
            user='User1',
            booked_at='2024-12-24T10:00:00Z'
        )
        Booking.objects.create(
            listing=listing2,
            user='User2',
            booked_at='2024-12-25T11:00:00Z'
        )

        # Create sample reviews
        Review.objects.create(
            listing=listing1,
            user='User1',
            rating=5,
            comment='Great place!',
            created_at='2024-12-24T12:00:00Z'
        )
        Review.objects.create(
            listing=listing2,
            user='User2',
            rating=4,
            comment='Nice experience.',
            created_at='2024-12-25T13:00:00Z'
        )

        self.stdout.write(self.style.SUCCESS('Database seeded successfully with listings, bookings, and reviews'))