from django.db import models
from django.core.validators import FileExtensionValidator
from accounts_app.models import Owner

# Create your models here.


# ------------------------------------------------------------> Requests, PropertyBuyImages, Witnesses, BuyProperty, PropertyPrice, Buyer, PropertyDeed, OwnerBuyProperty <------------------------------------------------------------

# Base Property model
class BaseProperty(models.Model):
    district_located = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    property_description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=255, default='Vacant', choices=(
        ('Vacant', 'Vacant'),
        ('Occupied', 'Occupied')
    ))
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class Request(models.Model):
    email_address = models.EmailField()
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    property_type = models.CharField(max_length=50, choices=(
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('buy_property', 'Buy Property'),
    ))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'requests'


class OwnerBuyProperty(models.Model):
    full_name = models.CharField(max_length=255)
    mother_name = models.CharField(max_length=255)
    identity = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=255)
    status = models.CharField(max_length=255, choices=(
        ('owner', 'Owner'),
        ('representor', 'Representor')
    ))
    image_path = models.ImageField(upload_to='owner_images/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='buy_properties')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'owner_buy_properties'


class Buyer(models.Model):
    full_name = models.CharField(max_length=255)
    mother_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=255)
    passport_no = models.CharField(max_length=255)
    signature = models.ImageField(upload_to='buyer_signatures/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    has_representor = models.BooleanField(default=False)
    image_path = models.ImageField(upload_to='buyer_images/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'buyers'


class Witness(models.Model):
    full_name = models.CharField(max_length=255)
    signature = models.ImageField(upload_to='witness_signatures/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    status = models.CharField(max_length=255, choices=(
        ('identity_guarantor', 'Identity Guarantor'),
        ('financial_guarantor', 'Financial Guarantor'),
    ))
    image_path = models.ImageField(upload_to='witness_images/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'witnesses'





class BuyProperty(models.Model):
    district_located = models.CharField(max_length=255)
    property_size = models.CharField(max_length=255)
    lotto_no = models.CharField(max_length=255)
    local_government = models.CharField(max_length=255)
    court_district = models.CharField(max_length=255)
    on_east = models.CharField(max_length=255)
    on_south = models.CharField(max_length=255)
    on_west = models.CharField(max_length=255)
    on_north = models.CharField(max_length=255)
    judge_person = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    property_status = models.CharField(max_length=255, choices=(
        ('available', 'Available'),
        ('unavailable', 'Unavailable')
    ))
    buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, blank=True, related_name='properties')
    owner_buy_property = models.ForeignKey(OwnerBuyProperty, on_delete=models.CASCADE, related_name='properties')
    witness = models.ForeignKey(Witness, on_delete=models.CASCADE, related_name='properties')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'buy_properties'

class PropertyBuyImage(models.Model):
    image_path = models.ImageField(upload_to='property_buy_images/')
    buy_property = models.ForeignKey(BuyProperty, on_delete=models.CASCADE, related_name='images')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'property_buy_images'
        
class PropertyPrice(models.Model):
    actual_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    buy_property = models.ForeignKey(BuyProperty, on_delete=models.CASCADE, related_name='prices')
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='prices')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'property_prices'




class PropertyDeed(models.Model):
    deed_number = models.CharField(max_length=255, unique=True)
    issue_date = models.DateField()
    buy_property = models.ForeignKey(BuyProperty, on_delete=models.CASCADE, related_name='deeds')
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='deeds')
    property_price = models.ForeignKey(PropertyPrice, on_delete=models.CASCADE, related_name='deeds')
    owner_buy_property = models.ForeignKey(OwnerBuyProperty, on_delete=models.CASCADE, related_name='deeds')
    witness = models.ForeignKey(Witness, on_delete=models.CASCADE, related_name='deeds')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'property_deeds'

