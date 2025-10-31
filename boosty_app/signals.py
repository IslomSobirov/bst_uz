import os
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from PIL import Image

from .models import Post, UserProfile


def resize_image(image_field, max_width, max_height, quality=85):
    """
    Resize an image field to specified dimensions while maintaining aspect ratio.
    Only resizes if the image is larger than the specified dimensions.
    Assumes the image_field has a valid file object.
    """
    try:
        # Open the image
        img = Image.open(image_field)

        # Convert RGBA to RGB if necessary (for JPEG compatibility)
        if img.mode in ("RGBA", "LA", "P"):
            # Create a white background
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # Check if resizing is needed
        if img.width <= max_width and img.height <= max_height:
            return

        # Calculate new dimensions maintaining aspect ratio
        ratio = min(max_width / img.width, max_height / img.height)
        new_width = int(img.width * ratio)
        new_height = int(img.height * ratio)

        # Resize image using high-quality resampling
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Save to BytesIO
        img_io = BytesIO()
        # Use JPEG format for better compression, unless original was PNG with transparency
        img_format = "JPEG"
        img.save(img_io, format=img_format, quality=quality, optimize=True)
        img_io.seek(0)

        # Get file extension - prefer .jpg for resized images
        filename = os.path.splitext(image_field.name)[0] + ".jpg"

        # Save the resized image back to the field
        image_field.save(filename, ContentFile(img_io.read()), save=False)
        img_io.close()
    except (IOError, OSError, ValueError, TypeError, AttributeError) as e:
        # If image processing fails (invalid image, unsupported format, etc.),
        # log error but don't break the save operation
        print(f"Error resizing image: {e}")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when a User is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when a User is saved"""
    if hasattr(instance, "profile"):
        instance.profile.save()


@receiver(pre_save, sender=UserProfile)
def resize_user_avatar(sender, instance, **kwargs):
    """Resize user avatar before saving"""
    if instance.avatar and instance.avatar.name:
        # Check if this is a new upload (file object exists)
        if hasattr(instance.avatar, "file") and instance.avatar.file:
            # Resize avatars to max 400x400 pixels
            resize_image(instance.avatar, max_width=400, max_height=400)


@receiver(pre_save, sender=Post)
def resize_post_image(sender, instance, **kwargs):
    """Resize post image before saving"""
    if instance.image and instance.image.name:
        # Check if this is a new upload (file object exists)
        if hasattr(instance.image, "file") and instance.image.file:
            # Resize post images to max 1200x1200 pixels
            resize_image(instance.image, max_width=1200, max_height=1200)
