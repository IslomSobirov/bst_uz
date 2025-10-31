"""
API tests for category endpoints
"""
import pytest
from rest_framework import status
from boosty_app.models import Category


@pytest.mark.django_db
class TestCategoryList:
    """Test category listing"""
    
    def test_list_categories(self, api_client, category):
        """Test listing all categories"""
        response = api_client.get('/api/categories/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
    
    def test_list_categories_unauthenticated(self, api_client, category):
        """Test listing categories without authentication"""
        response = api_client.get('/api/categories/')
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestCategoryCreate:
    """Test category creation"""
    
    def test_create_category_authenticated(self, authenticated_client):
        """Test creating a category when authenticated"""
        data = {
            'name': 'Science',
            'description': 'Science related content'
        }
        response = authenticated_client.post('/api/categories/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Science'
    
    def test_create_category_unauthenticated(self, api_client):
        """Test creating category without authentication"""
        data = {
            'name': 'Science',
            'description': 'Science related content'
        }
        response = api_client.post('/api/categories/', data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_duplicate_category(self, authenticated_client, category):
        """Test creating duplicate category"""
        data = {
            'name': category.name,  # Same name
            'description': 'Different description'
        }
        response = authenticated_client.post('/api/categories/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data
    
    def test_create_category_missing_fields(self, authenticated_client):
        """Test creating category with missing required fields"""
        data = {
            'description': 'No name provided'
        }
        response = authenticated_client.post('/api/categories/', data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCategoryDetail:
    """Test category detail endpoint"""
    
    def test_get_category_detail(self, api_client, category):
        """Test getting a specific category"""
        response = api_client.get(f'/api/categories/{category.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == category.name
    
    def test_get_nonexistent_category(self, api_client):
        """Test getting non-existent category"""
        response = api_client.get('/api/categories/9999/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_category(self, authenticated_client, category):
        """Test updating a category"""
        data = {
            'name': 'Updated Technology',
            'description': 'Updated description'
        }
        response = authenticated_client.put(f'/api/categories/{category.id}/', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Technology'
    
    def test_delete_category(self, authenticated_client, category):
        """Test deleting a category"""
        category_id = category.id
        response = authenticated_client.delete(f'/api/categories/{category_id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(id=category_id).exists()
    
    def test_delete_category_unauthenticated(self, api_client, category):
        """Test deleting category without authentication"""
        response = api_client.delete(f'/api/categories/{category.id}/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

