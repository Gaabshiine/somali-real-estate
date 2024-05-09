from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Owner(models.Model):
    first_name = models.CharField(max_length=255, blank=False, null=False)
    middle_name = models.CharField(max_length=25, blank=False, null=False)
    last_name = models.CharField(max_length=255, blank=False, null=False)
    email_address = models.EmailField()
    password = models.CharField(max_length=128)  # Storing hashed passwords
    phone_number = models.CharField(max_length=25)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=255, default='unspecified')
    state = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    occupation = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    class Meta:
        db_table = 'owner'

class Tenant(models.Model):
    first_name = models.CharField(max_length=255, blank=False, null=False)
    middle_name = models.CharField(max_length=25, blank=False, null=False)
    last_name = models.CharField(max_length=255, blank=False, null=False)
    email_address = models.EmailField()
    password = models.CharField(max_length=128)  # Storing hashed passwords
    phone_number = models.CharField(max_length=25)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=255, default='unspecified')
    state = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    occupation = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    class Meta:
        db_table = 'tenant'
