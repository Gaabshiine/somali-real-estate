from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class AdminManager(BaseUserManager):
    def create_admin(self, email, full_name, password=None, is_superuser=False, **extra_fields):
        """
        Creates and saves an Admin with the given email, full name, password, and extra fields.
        """
        if not email:
            raise ValueError("Admin must have an email address")
        if not full_name:
            raise ValueError("Admin must have a full name")

        admin = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            is_superuser=is_superuser,
            **extra_fields
        )
        admin.set_password(password)
        admin.is_admin = True  # Assuming all created admins are also "admin"
        admin.is_staff = True  # Assuming all created admins are also "staff"
        admin.save(using=self._db)
        return admin

class Admin(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=200)
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    address = models.CharField(max_length=255)
    gender = models.CharField(max_length=50, choices=(
        ('male', 'Male'), ('female', 'Female')
    ))
    phone_number = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    

    objects = AdminManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
    
    class Meta:
        db_table = 'admins'

class AdminActivityLog(models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
    action = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log by {self.admin.email} at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"



