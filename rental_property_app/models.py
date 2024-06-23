from django.db import models
from accounts_app.models import Owner, Tenant
from django.core.validators import FileExtensionValidator



"""
Manages the details of apartments
"""

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



# # Manages individual rooms within apartments.
# class Room(models.Model):
#     room_name = models.CharField(max_length=255)
#     room_type = models.CharField(max_length=255, choices=(
#         ('master', 'Master Room'),
#         ('single', 'Single Room'),
#         ('one_bedroom', 'One Bedroom'),
#         ('two_bedroom', 'Two Bedroom'),
#         ('three_bedroom', 'Three Bedroom'),
#     ))
#     floor_number = models.IntegerField()
#     rent_amount = models.DecimalField(max_digits=8, decimal_places=2)
#     deposit_amount = models.DecimalField(max_digits=8, decimal_places=2)
#     room_description = models.TextField(blank=True, null=True)
#     room_image = models.ImageField(upload_to='room_images/', null=True, blank=True)
#     status = models.CharField(max_length=255, default='Vacant', choices=(
#         ('Vacant', 'Vacant'),
#         ('Occupied', 'Occupied')
#     ))
#     apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='rooms')
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         db_table = 'rooms'

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         self.apartment.update_status()




# # Links tenants to specific rooms for a duration.
# class RoomAssignment(models.Model):
#     move_in_date = models.DateField()
#     move_out_date = models.DateField(null=True, blank=True)
#     room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='assignments')
#     tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='room_assignments')
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         db_table = 'room_assignments'



# # Manages complaints specifically associated with rooms.
# class RoomComplaints(models.Model):
#     complaint_type = models.CharField(max_length=255)
#     complaint_description = models.TextField()
#     complaint_status = models.CharField(max_length=255, default='Unresolved', choices=(
#         ('Unresolved', 'Unresolved'),
#         ('In Progress', 'In Progress'),
#         ('Resolved', 'Resolved')
#     ))
#     room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='complaints')
#     tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='complaints')
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         db_table = 'room_complaints'


# # Manages financial transactions associated with room rentals.
# class RoomInvoice(models.Model):
#     invoice_number = models.CharField(max_length=255, unique=True) # Unique invoice number for each invoice generated
#     amount_due = models.DecimalField(max_digits=8, decimal_places=2)
#     amount_paid = models.DecimalField(max_digits=8, decimal_places=2)
#     rest_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
#     invoice_status = models.CharField(max_length=255, default='Pending', choices=(
#         ('Paid', 'Paid'),
#         ('Pending', 'Pending'),
#         ('Overdue', 'Overdue')
#     ))
#     tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, related_name='invoices')
#     room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='invoices')
#     invoice_date = models.DateField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         db_table = 'room_invoices'


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
    owner = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='identification')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tenant_identifications'

    def __str__(self):
        return f"{self.identification_number} ({self.document_type})"










