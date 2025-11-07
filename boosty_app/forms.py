"""Forms for creator dashboard"""

from django import forms

from .models import Category, Post, SubscriptionTier


class PostForm(forms.ModelForm):
    """Form for creating and editing posts"""

    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'image', 'status', 'is_free', 'tiers']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter post title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Enter post content'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'is_free': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tiers': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all().order_by('name')
        self.fields['category'].empty_label = 'No category'

        # Filter tiers to only show user's own tiers
        if user:
            self.fields['tiers'].queryset = SubscriptionTier.objects.filter(
                creator=user.profile, is_active=True
            ).order_by('order', 'price')
        else:
            self.fields['tiers'].queryset = SubscriptionTier.objects.none()

        # Make tiers optional
        self.fields['tiers'].required = False
        self.fields['tiers'].help_text = 'Select which tiers can access this post. Leave empty if post is free.'


class SubscriptionTierForm(forms.ModelForm):
    """Form for creating and editing subscription tiers"""

    class Meta:
        model = SubscriptionTier
        fields = ['name', 'description', 'price', 'image', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Basic, Premium, VIP'}),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Describe what subscribers will get with this tier...',
                }
            ),
            'price': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': '9.99', 'step': '0.01', 'min': '0.01'}
            ),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'order': 'Lower numbers appear first',
            'price': 'Monthly price in USD',
        }
