from django.db import models
from accounts_app.models import Owner, Tenant
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from datetime import datetime



"""
Manages the details of apartments
"""
# ------------------------------------------------------------>  Apartment, Images, Features, Room, RoomAssignment, RoomComplaints, RoomInvoice <------------------------------------------------------------
# Apartment Model
class Apartment(models.Model):
    apartment_name = models.CharField(max_length=255)
    year_built = models.IntegerField()
    area = models.DecimalField(max_digits=8, decimal_places=2)
    district_located = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    apartment_description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=255, default='Vacant', choices=(
        ('Vacant', 'Vacant'),
        ('Occupied', 'Occupied')
    ))
    video = models.FileField(upload_to='apartment_videos/', blank=True, null=True)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'apartments'

    def update_status(self):
        if self.rooms.filter(status='Vacant').exists():
            self.status = 'Vacant'
        else:
            self.status = 'Occupied'
        self.save()



# Manages images for apartments.
class ApartmentImages(models.Model):
    image = models.ImageField(upload_to='apartment_images/')
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='images')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'apartment_images'


# Manages various amenities associated with an apartment.
class ApartmentFeature(models.Model):
    has_gym = models.BooleanField(default=False)
    has_car_parking = models.BooleanField(default=False)
    has_internet = models.BooleanField(default=False)
    has_swimming_pool = models.BooleanField(default=False)
    has_alarm = models.BooleanField(default=False)
    has_air_conditioner = models.BooleanField(default=False)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='features')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'apartment_features'


# Manages rooms within apartments.
class Room(models.Model):
    room_name = models.CharField(max_length=255)
    room_type = models.CharField(max_length=255, choices=(
        ('master', 'Master Room'),
        ('single', 'Single Room'),
        ('one_bedroom', 'One Bedroom'),
        ('two_bedroom', 'Two Bedroom'),
        ('three_bedroom', 'Three Bedroom'),
    ))
    floor_number = models.IntegerField()
    rent_amount = models.DecimalField(max_digits=8, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=8, decimal_places=2)
    room_description = models.TextField(blank=True, null=True)
    room_image = models.ImageField(upload_to='room_images/', null=True, blank=True)
    status = models.CharField(max_length=255, default='Vacant', choices=(
        ('Vacant', 'Vacant'),
        ('Occupied', 'Occupied')
    ))
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rooms'


# Room Assignment Model
class RoomAssignment(models.Model):
    move_in_date = models.DateField()
    move_out_date = models.DateField(null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='assignments')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='room_assignments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'room_assignments'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_room_status()
        
    def update_room_status(self):
        if self.move_out_date and isinstance(self.move_out_date, str):
            self.move_out_date = datetime.strptime(self.move_out_date, "%Y-%m-%d").date()
        
        if self.move_out_date and self.move_out_date <= timezone.now().date():
            self.room.status = 'Vacant'
        else:
            self.room.status = 'Occupied'
        self.room.save()
        self.room.apartment.update_status()

# Manages complaints specifically associated with rooms.
class RoomComplaints(models.Model):
    complaint_type = models.CharField(max_length=255)
    complaint_description = models.TextField()
    complaint_status = models.CharField(max_length=255, default='Unresolved', choices=(
        ('Unresolved', 'Unresolved'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved')
    ))
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='complaints')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='complaints')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'room_complaints'


# Manages invoices for rooms.
class RoomInvoice(models.Model):
    invoice_number = models.CharField(max_length=12, unique=True, editable=False, default='')
    amount_due = models.DecimalField(max_digits=8, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)
    rest_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    invoice_status = models.CharField(max_length=255, default='Pending', choices=(
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Overdue', 'Overdue')
    ))
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='invoices')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='invoices')
    invoice_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'room_invoices'




"""
End: the details of apartments
"""





"""
Start: Identifies the tenants and the owner of the property
"""
class OwnerIdentification(models.Model):
    document_type = models.CharField(max_length=255, help_text="Type of identification document (e.g., Passport, Driver's License)")
    identification_number = models.CharField(max_length=255, help_text="Identification number")
    document_file = models.FileField(
        upload_to='identification_docs/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'jpg', 'jpeg', 'png'])],
        help_text="Upload a scan or photo of the identification document."
    )
    owner = models.OneToOneField(Owner, on_delete=models.CASCADE, related_name='identification')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'owner_identifications'

    def __str__(self):
        return f"{self.identification_number} ({self.document_type})"


class TenantIdentification(models.Model):
    document_type = models.CharField(max_length=255, help_text="Type of identification document (e.g., Passport, Driver's License)")
    identification_number = models.CharField(max_length=255, help_text="Identification number")
    document_file = models.FileField(
        upload_to='identification_docs/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'jpg', 'jpeg', 'png'])],
        help_text="Upload a scan or photo of the identification document."
    )
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='identification')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tenant_identifications'

    def __str__(self):
        return f"{self.identification_number} ({self.document_type})"


""" 
End: Identifies the tenants and the owner of the property
"""


"""
Start: Manages the detail of the house
"""

# ------------------------------------------------------------> House, HouseAssignment, HouseInvoice, HouseImage, HouseComplaints <------------------------------------------------------------

class House(models.Model):
    house_name = models.CharField(max_length=255)
    rent_amount = models.DecimalField(max_digits=8, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=8, decimal_places=2)
    year_built = models.IntegerField()
    area = models.DecimalField(max_digits=8, decimal_places=2)
    district_located = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    house_description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=255, default='Vacant', choices=(
        ('Vacant', 'Vacant'),
        ('Occupied', 'Occupied')
    ))
    no_of_bathrooms = models.IntegerField()
    no_of_rooms = models.IntegerField()
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='houses')
    created_at = models.DateTimeField(auto_now_add=True)

    def update_status(self):
        if self.assignments.filter(move_out_date__isnull=True).exists():
            self.status = 'Occupied'
        else:
            self.status = 'Vacant'
        self.save()

    class Meta:
        db_table = 'houses'

    

class HouseAssignment(models.Model):
    move_in_date = models.DateField()
    move_out_date = models.DateField(null=True, blank=True)
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='assignments')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='house_assignments')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.house.update_status()
        

    class Meta:
        db_table = 'house_assignments'



class HouseInvoice(models.Model):
    invoice_number = models.CharField(max_length=12, unique=True, editable=False, default='')
    amount_due = models.DecimalField(max_digits=8, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)
    rest_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    invoice_status = models.CharField(max_length=255, default='Pending', choices=(
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Overdue', 'Overdue')
    ))
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='house_invoices')
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='invoices')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'house_invoices'


class HouseImage(models.Model):
    image = models.ImageField(upload_to='house_images/')
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='images')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'house_images'


class HouseComplaints(models.Model):
    complaint_type = models.CharField(max_length=255)
    complaint_description = models.TextField()
    complaint_status = models.CharField(max_length=255, default='Unresolved', choices=(
        ('Unresolved', 'Unresolved'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved')
    ))
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='complaints')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='house_complaints')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'house_complaints'




