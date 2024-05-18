from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.conf import settings

class Owner(AbstractBaseUser):
    first_name = models.CharField(max_length=255, blank=False, null=False)
    middle_name = models.CharField(max_length=25, blank=False, null=False)
    last_name = models.CharField(max_length=255, blank=False, null=False)
    email_address = models.EmailField(unique=True)  # Ensure unique email addresses
    password = models.CharField(max_length=128)  # Storing passwords in plain text
    phone_number = models.CharField(max_length=25)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=255, default='unspecified')
    state = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    occupation = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)  # Add last_login field

    USERNAME_FIELD = 'email_address'  # Specify the field to use for authentication
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Specify other required fields

    class Meta:
        db_table = 'owner'

class Tenant(AbstractBaseUser):
    first_name = models.CharField(max_length=255, blank=False, null=False)
    middle_name = models.CharField(max_length=25, blank=False, null=False)
    last_name = models.CharField(max_length=255, blank=False, null=False)
    email_address = models.EmailField(unique=True)  # Ensure unique email addresses
    password = models.CharField(max_length=128)  # Storing passwords in plain text
    phone_number = models.CharField(max_length=25)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=255, default='unspecified')
    state = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    occupation = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)  # Add last_login field

    USERNAME_FIELD = 'email_address'  # Specify the field to use for authentication
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Specify other required fields

    class Meta:
        db_table = 'tenant'




class Profile(models.Model):
    owner = models.OneToOneField('Owner', on_delete=models.CASCADE, null=True, blank=True)
    tenant = models.OneToOneField('Tenant', on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    bio = models.TextField(blank=True)
    social_media_link = models.URLField(blank=True)
    facebook_link = models.URLField(blank=True)
    tiktok_link = models.URLField(blank=True)
    youtube_link = models.URLField(blank=True)

    def get_image_url(self):
        if self.image:
            return self.image.url
        
        user = self.owner if self.owner else self.tenant
        if user.gender == 'male':
            return '/static/user_styles/images/avatar_man.png'
        else:
            return '/static/user_styles/images/avatar_woman.png'
    def get_user(self):
        return self.owner or self.tenant