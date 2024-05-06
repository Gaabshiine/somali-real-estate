from django.db import models

# Create your models here.


class Owner(models.Model):
    first_name=models.CharField(max_length=255, blank=False, null=False)
    middle_name=models.CharField(max_length=25,blank=False, null=False)
    last_name=models.CharField(max_length=255, blank=False, null=False)
    email_address=models.EmailField()
    password=models.CharField(max_length=50)
    phone_number=models.CharField(max_length=25)
    date_of_birth=models.DateField()
    gender = models.CharField(max_length=255, default='unspecified')
    state = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    occupation = models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta():
        db_table = 'owner'


# tenant model
class Tenant(models.Model):
    first_name=models.CharField(max_length=255, blank=False, null=False)
    middle_name=models.CharField(max_length=25,blank=False, null=False)
    last_name=models.CharField(max_length=255, blank=False, null=False)
    email_address=models.EmailField()
    password=models.CharField(max_length=50)
    phone_number=models.CharField(max_length=25)
    date_of_birth=models.DateField()
    gender = models.CharField(max_length=255, default='unspecified')
    state = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    occupation = models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta():
        db_table = 'tenant'






