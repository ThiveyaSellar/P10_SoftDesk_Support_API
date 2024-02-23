from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings

class User(AbstractUser):
    # La classe AbstractUser contient tous les champs de la classe User
    # entre autres champs nom d'utilisateur et mot de passe (identifants)
    created_time = models.DateTimeField(auto_now_add=True)
    age = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(15), MaxValueValidator(100)]
    )
    can_be_contacted = models.BooleanField()
    can_data_be_shared = models.BooleanField()


class Contributor(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

class Project(models.Model):

    BACK_END = "BACK_END"
    FRONT_END = "FRONT_END"
    IOS = "IOS"
    ANDROID = "ANDROID"

    TYPE_CHOICES = (
        (BACK_END, "Back-end"),
        (FRONT_END, "Front-end"),
        (IOS, "iOS"),
        (ANDROID, "Android"),
    )
    created_time = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    contributors = models.ManyToManyField(Contributor)
    name = models.CharField(max_length=128)
    description = models.TextField(max_length=2048)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)


class Issue(models.Model):

    # Status
    TO_DO = "TO_DO"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"
    # Priority
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    # Tag
    BUG = "BUG"
    FEATURE = "FEATURE"
    TASK = "TASK"

    STATUS_CHOICES = (
        (TO_DO, 'To do'),
        (IN_PROGRESS, 'In progress'),
        (FINISHED, 'Finished')
    )
    PRIORITY_CHOICES = (
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High")
    )
    TAG_CHOICES = (
        (BUG, "Bug"),
        (FEATURE, "Feature"),
        (TASK, "Task")
    )

    created_time = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Contributor,on_delete=models.CASCADE)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.TextField(max_length=2048)
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=TO_DO
    )
    priority = models.CharField(max_length=30,choices=PRIORITY_CHOICES)
    tag = models.CharField(max_length=30,choices=TAG_CHOICES)

class Comment(models.Model):

    created_time = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Contributor,on_delete=models.CASCADE)
    description = models.TextField(max_length=2048)
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue,on_delete=models.CASCADE)
