from django.db import models
from django.contrib.auth.models import AbstractBaseUser

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
