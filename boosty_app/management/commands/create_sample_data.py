import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker

from boosty_app.models import Category, Comment, Post, Subscription, UserProfile


class Command(BaseCommand):
    help = 'Create sample data for the enhanced creator system'

    def add_arguments(self, parser):
        parser.add_argument('--creators', type=int, default=5, help='Number of creators to create')
        parser.add_argument('--users', type=int, default=10, help='Number of regular users to create')
        parser.add_argument('--posts', type=int, default=30, help='Number of posts to create')
        parser.add_argument('--comments', type=int, default=80, help='Number of comments to create')

    def handle(self, *args, **options):
        fake = Faker()

        self.stdout.write(self.style.SUCCESS('Creating sample data for the creator system...'))

        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin', email='admin@example.com', password='admin123', first_name='Admin', last_name='User'
            )
            admin.profile.is_creator = True
            admin.profile.bio = 'Platform administrator and content creator'
            admin.profile.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin creator: admin (password: admin123)'))

        # Create creators
        creators = []
        for i in range(options['creators']):
            username = fake.user_name()
            while User.objects.filter(username=username).exists():
                username = fake.user_name()

            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )

            # Make them creators
            user.profile.is_creator = True
            user.profile.bio = fake.text(max_nb_chars=200)
            user.profile.save()

            creators.append(user)

        self.stdout.write(self.style.SUCCESS(f'Created {len(creators)} creators'))

        # Create regular users
        users = []
        for i in range(options['users']):
            username = fake.user_name()
            while User.objects.filter(username=username).exists():
                username = fake.user_name()

            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )

            # Regular users
            user.profile.bio = fake.text(max_nb_chars=150)
            user.profile.save()

            users.append(user)

        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} regular users'))

        # Add admin to creators list
        admin_user = User.objects.get(username='admin')
        creators.append(admin_user)
        users.append(admin_user)

        # Create categories if they don't exist
        category_names = [
            'Technology',
            'Travel',
            'Food',
            'Lifestyle',
            'Business',
            'Health',
            'Education',
            'Entertainment',
            'Sports',
            'Science',
        ]

        categories = []
        for name in category_names:
            category, created = Category.objects.get_or_create(
                name=name, defaults={'description': fake.text(max_nb_chars=200)}
            )
            categories.append(category)

        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))

        # Create posts from creators
        posts = []
        for i in range(options['posts']):
            creator = random.choice(creators)
            status = random.choices(['draft', 'published', 'published'], weights=[1, 3, 1])[0]
            # Make approximately 30% of published posts free
            is_free = status == 'published' and random.random() < 0.3

            post = Post.objects.create(
                title=fake.sentence(nb_words=6)[:-1],
                content=fake.text(max_nb_chars=800),
                author=creator,
                category=random.choice(categories),
                image=None,  # No images for now
                status=status,
                is_free=is_free,
            )
            posts.append(post)

        self.stdout.write(self.style.SUCCESS(f'Created {len(posts)} posts'))

        # Create comments
        published_posts = [post for post in posts if post.status == 'published']
        all_users = creators + users

        comments = []
        for i in range(options['comments']):
            if published_posts:
                comment = Comment.objects.create(
                    post=random.choice(published_posts),
                    author=random.choice(all_users),
                    content=fake.text(max_nb_chars=200),
                )
                comments.append(comment)

        self.stdout.write(self.style.SUCCESS(f'Created {len(comments)} comments'))

        # Create subscriptions (users following creators)
        subscriptions = []
        for user in users:
            # Each user follows 2-4 random creators
            num_following = random.randint(2, 4)
            creators_to_follow = random.sample(creators, min(num_following, len(creators)))

            for creator in creators_to_follow:
                if creator != user:
                    subscription, created = Subscription.objects.get_or_create(subscriber=user, creator=creator.profile)
                    if created:
                        subscriptions.append(subscription)

        self.stdout.write(self.style.SUCCESS(f'Created {len(subscriptions)} subscriptions'))

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSample data created successfully!\n'
                f'Creators: {len(creators)}\n'
                f'Regular Users: {len(users)}\n'
                f'Categories: {len(categories)}\n'
                f'Posts: {len(posts)} (Draft: {len([p for p in posts if p.status == "draft"])}, '
                f'Published: {len([p for p in posts if p.status == "published"])}, '
                f'Free: {len([p for p in posts if p.is_free])})\n'
                f'Comments: {len(comments)}\n'
                f'Subscriptions: {len(subscriptions)}\n\n'
                f'Admin credentials:\n'
                f'Username: admin\n'
                f'Password: admin123\n'
                f'Admin URL: http://localhost:8000/admin/\n\n'
                f'API Endpoints:\n'
                f'Creators: http://localhost:8000/api/profiles/creators/\n'
                f'Posts: http://localhost:8000/api/posts/\n'
                f'Register: http://localhost:8000/api/auth/register/\n'
                f'Login: http://localhost:8000/api/auth/login/\n'
            )
        )
