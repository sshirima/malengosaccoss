from django.db import models
from django.contrib import auth
import uuid
from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
    _user_has_perm,
    _user_has_module_perms,
)

# Create your models here.

class UserManager(BaseUserManager):
    
    def create_user(self, email, password=None, is_admin=False, is_staff=False, is_active=True):
        if not email:
            raise ValueError("User must have an email")

        if not password:
            raise ValueError("User must have a password")
        

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)  # change password to hash
        user.is_admin = is_admin
        user.is_staff = is_staff
        user.is_active = is_active
        user.save(using=self._db)
        return user
        
    def create_superuser(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    id = models.UUIDField(primary_key = True,default = uuid.uuid4, editable = False)
    username = models.CharField(max_length=40, unique=False, default='')
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()


    def get_full_name(self):
        """
        Return the first name and last name
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Since the user is identified by their email address return that
        """
        return self.email

    
    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has the given permission
        """
        if self.is_active and self.is_admin:
            return True

        return _user_has_perm(self, perm, obj)


    def has_perms(self, perm_list, obj=None):
        """
        Returns True if the user has each of the permissions in the give list
        """
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the give app label
        """
        if self.is_active and self.is_admin:
            return True

        return _user_has_module_perms(self, app_label)
