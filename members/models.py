from django.db import models
import uuid

from authentication.models import User
# Create your models here.

# Create your models here.
GENDER_STATUS = (
    ('male', 'Male' ),
    ('female', 'Female' ),
)

class Member(models.Model):
    id = models.UUIDField(primary_key = True,default = uuid.uuid4, editable = False)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=False)
    middle_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    gender = models.CharField(max_length=20, choices=GENDER_STATUS)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['first_name','middle_name', 'last_name']

    def __str__(self):
       return str('{} {}'.format(self.first_name, self.last_name))

    def get_full_name(self):
        """
        Return the first name and last name
        """
        full_name = '%s %s %s' % (self.first_name, self.middle_name,self.last_name)
        return full_name.strip()

