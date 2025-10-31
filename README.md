# Boosty Uzbekistan - Full Stack Web Application

A modern web application built with Django REST Framework backend and React frontend, featuring a blog/content management system.

## 🚀 Features

- **Django Backend**: RESTful API with PostgreSQL database
- **React Frontend**: Modern, responsive user interface
- **Content Management**: Posts, categories, and comments system
- **User Authentication**: Built-in Django admin and user management
- **Docker Support**: Easy deployment with Docker Compose
- **Nginx**: Production-ready reverse proxy

## 🏗️ Architecture

```
boosty-uz/
├── backend/                 # Django application
│   ├── boosty_project/     # Main Django project
│   ├── boosty_app/         # Main Django app
│   ├── manage.py           # Django management script
│   └── requirements.txt    # Python dependencies
├── frontend/               # React application
│   ├── src/                # React source code
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
├── docker-compose.yml      # Docker services configuration
├── nginx.conf              # Nginx configuration
└── README.md               # This file
```

## 🛠️ Tech Stack

### Backend
- **Django 4.2+**: Web framework
- **Django REST Framework**: API framework
- **PostgreSQL**: Database
- **Django CORS Headers**: Cross-origin resource sharing
- **WhiteNoise**: Static file serving

### Frontend
- **React 18**: Frontend framework
- **React Scripts**: Build tools
- **Axios**: HTTP client

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Web server and reverse proxy

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git

### 1. Clone the repository
```bash
git clone <repository-url>
cd boosty-uz
```

### 2. Start the application
```bash
docker-compose up --build
```

### 3. Access the application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **Nginx**: http://localhost:80

## 📚 API Endpoints

### Authentication
- `GET /api/users/me/` - Get current user info
- `GET /api/auth/` - Django REST Framework browsable API

### Content Management
- `GET /api/categories/` - List all categories
- `POST /api/categories/` - Create new category
- `GET /api/posts/` - List published posts
- `POST /api/posts/` - Create new post
- `GET /api/posts/{id}/` - Get specific post
- `POST /api/posts/{id}/publish/` - Publish draft post
- `GET /api/posts/{id}/comments/` - Get post comments
- `POST /api/comments/` - Create new comment

## 🗄️ Database Models

### User
- Standard Django User model with authentication

### Category
- `name`: Category name
- `description`: Category description
- `created_at`, `updated_at`: Timestamps

### Post
- `title`: Post title
- `content`: Post content
- `author`: Foreign key to User
- `category`: Foreign key to Category
- `image`: Optional image upload
- `is_published`: Publication status
- `created_at`, `updated_at`: Timestamps

### Comment
- `post`: Foreign key to Post
- `author`: Foreign key to User
- `content`: Comment content
- `created_at`, `updated_at`: Timestamps

## 🔧 Development

### Running Django commands
```bash
docker-compose exec backend python manage.py [command]
```

### Creating Django superuser
```bash
docker-compose exec backend python manage.py createsuperuser
```

### Running migrations
```bash
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

### Collecting static files
```bash
docker-compose exec backend python manage.py collectstatic
```

## 🌐 Environment Variables

Create a `config.env` file with the following variables:

```env
SECRET_KEY=your-secret-key-here
DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
POSTGRES_DB=boosty_db
POSTGRES_USER=boosty_user
POSTGRES_PASSWORD=boosty_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
REACT_APP_API_URL=http://localhost:8000
```

## 📁 Project Structure

```
boosty-uz/
├── boosty_project/         # Django project settings
│   ├── __init__.py
│   ├── settings.py         # Django settings
│   ├── urls.py            # Main URL configuration
│   ├── wsgi.py            # WSGI application
│   └── asgi.py            # ASGI application
├── boosty_app/            # Main Django application
│   ├── __init__.py
│   ├── admin.py           # Admin interface
│   ├── apps.py            # App configuration
│   ├── models.py          # Database models
│   ├── serializers.py     # API serializers
│   ├── urls.py            # App URL configuration
│   └── views.py           # API views
├── frontend/              # React application
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   ├── App.css        # Component styles
│   │   ├── index.js       # React entry point
│   │   └── index.css      # Global styles
│   ├── public/
│   │   ├── index.html     # HTML template
│   │   ├── manifest.json  # Web app manifest
│   │   └── favicon.ico    # Favicon
│   ├── Dockerfile         # Frontend container
│   └── package.json       # Node.js dependencies
├── static/                # Django static files
├── media/                 # User uploaded files
├── docker-compose.yml     # Docker services
├── Dockerfile             # Backend container
├── nginx.conf             # Nginx configuration
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## 🚀 Deployment

### Production Considerations
1. Set `DEBUG=False` in production
2. Use strong `SECRET_KEY`
3. Configure proper `ALLOWED_HOSTS`
4. Set up SSL/TLS certificates
5. Use production database credentials
6. Configure proper static file serving

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions, please open an issue in the repository.
