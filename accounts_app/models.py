from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.conf import settings
from admin_dashboard.models import Admin


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
    created_at = models.DateTimeField(auto_now_add=True)  # Add created_at field
    last_login = models.DateTimeField(auto_now=True)  # Add last_login field

    USERNAME_FIELD = 'email_address'  # Specify the field to use for authentication
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Specify other required fields

    class Meta:
        db_table = 'owners'

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
    created_at = models.DateTimeField(auto_now_add=True)  # Add created_at field
    last_login = models.DateTimeField(auto_now=True)  # Add last_login field

    USERNAME_FIELD = 'email_address'  # Specify the field to use for authentication
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Specify other required fields

    class Meta:
        db_table = 'tenants'

class Profile(models.Model):
    profile_picture = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    bio = models.TextField(blank=True)
    facebook_link = models.URLField(blank=True)
    tiktok_link = models.URLField(blank=True)
    youtube_link = models.URLField(blank=True)
    person_id = models.PositiveIntegerField()
    person_type = models.CharField(max_length=10, choices=(
        ('owner', 'Owner'), 
        ('tenant', 'Tenant'),
        ('admin', 'Admin')
        ))
    created_at = models.DateTimeField(auto_now_add=True)

    def get_user(self):
        if self.person_type == 'owner':
            return Owner.objects.get(id=self.person_id)
        elif self.person_type == 'tenant':
            return Tenant.objects.get(id=self.person_id)
        elif self.person_type == 'admin':
            return Admin.objects.get(id=self.person_id)

    def get_image_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        else:
            user = self.get_user()
            if user.gender == 'male':
                return '/static/user_styles/images/avatar_man.png'
            else:
                return '/static/user_styles/images/avatar_woman.png'
            
    class Meta:
        db_table = 'profiles'


    


















