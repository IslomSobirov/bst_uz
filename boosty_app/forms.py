"""Forms for creator dashboard"""

from django import forms

from .models import Category, Post


class PostForm(forms.ModelForm):
    """Form for creating and editing posts"""

    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'image', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter post title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Enter post content'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all().order_by('name')
        self.fields['category'].empty_label = 'No category'
        # Remove is_free field since we only show posts to subscribers now
        if 'is_free' in self.fields:
            del self.fields['is_free']
