from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from boosty_app.models import Category, Post, Comment
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Create dummy data for testing'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=5, help='Number of users to create')
        parser.add_argument('--categories', type=int, default=5, help='Number of categories to create')
        parser.add_argument('--posts', type=int, default=20, help='Number of posts to create')
        parser.add_argument('--comments', type=int, default=50, help='Number of comments to create')

    def handle(self, *args, **options):
        fake = Faker()
        
        self.stdout.write(self.style.SUCCESS('Creating dummy data...'))
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS(f'Created superuser: admin (password: admin123)'))
        
        # Create users
        users = []
        for i in range(options['users']):
            username = fake.user_name()
            # Ensure username is unique
            while User.objects.filter(username=username).exists():
                username = fake.user_name()
            
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            users.append(user)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} users'))
        
        # Add admin to users list
        admin_user = User.objects.get(username='admin')
        users.append(admin_user)
        
        # Create categories
        categories = []
        category_names = [
            'Technology', 'Travel', 'Food', 'Lifestyle', 'Business',
            'Health', 'Education', 'Entertainment', 'Sports', 'Science'
        ]
        
        for i in range(min(options['categories'], len(category_names))):
            category, created = Category.objects.get_or_create(
                name=category_names[i],
                defaults={'description': fake.text(max_nb_chars=200)}
            )
            categories.append(category)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))
        
        # Create posts
        posts = []
        for i in range(options['posts']):
            post = Post.objects.create(
                title=fake.sentence(nb_words=6)[:-1],  # Remove the period
                content=fake.text(max_nb_chars=1000),
                author=random.choice(users),
                category=random.choice(categories),
                is_published=random.choice([True, True, True, False])  # 75% published
            )
            posts.append(post)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(posts)} posts'))
        
        # Create comments
        published_posts = [post for post in posts if post.is_published]
        comments = []
        
        for i in range(options['comments']):
            if published_posts:  # Only create comments for published posts
                comment = Comment.objects.create(
                    post=random.choice(published_posts),
                    author=random.choice(users),
                    content=fake.text(max_nb_chars=300)
                )
                comments.append(comment)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(comments)} comments'))
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nDummy data created successfully!\n'
                f'Users: {User.objects.count()}\n'
                f'Categories: {Category.objects.count()}\n'
                f'Posts: {Post.objects.count()}\n'
                f'Published Posts: {Post.objects.filter(is_published=True).count()}\n'
                f'Comments: {Comment.objects.count()}\n\n'
                f'Admin credentials:\n'
                f'Username: admin\n'
                f'Password: admin123\n'
                f'Admin URL: http://localhost:8000/admin/\n'
            )
        )
