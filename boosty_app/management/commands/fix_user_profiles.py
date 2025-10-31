from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from boosty_app.models import UserProfile


class Command(BaseCommand):
    help = 'Fix existing users who do not have UserProfile objects'

    def handle(self, *args, **options):
        self.stdout.write('Fixing user profiles...')

        users_without_profiles = []
        for user in User.objects.all():
            try:
                # Try to access the profile
                user.profile
            except UserProfile.DoesNotExist:
                users_without_profiles.append(user)

        if users_without_profiles:
            self.stdout.write(f'Found {len(users_without_profiles)} users without profiles')

            for user in users_without_profiles:
                UserProfile.objects.create(user=user)
                self.stdout.write(f'Created profile for user: {user.username}')
        else:
            self.stdout.write('All users have profiles')

        self.stdout.write(self.style.SUCCESS('User profile fix completed!'))
