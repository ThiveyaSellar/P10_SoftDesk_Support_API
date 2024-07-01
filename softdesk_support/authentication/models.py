from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class User(AbstractUser):

    created_time = models.DateTimeField(auto_now_add=True)
    age = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(15), MaxValueValidator(100)]
    )
    can_be_contacted = models.BooleanField()
    can_data_be_shared = models.BooleanField()

    is_active = True

    REQUIRED_FIELDS = ['age', 'can_be_contacted', 'can_data_be_shared']
