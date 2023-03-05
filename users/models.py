from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Create your models here.
class User(AbstractUser):
    
    class Types(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        ELDER = "ELDER", "Elder"
        RELATED = "ELDER_RELATED", "Elder_related"
        SOCIAL_WORKER = "SOCIAL_WORKER", "Social_worker"
    
    base_type = Types.ADMIN

    type = models.CharField(_("Type"), 
                            max_length=50, 
                            choices=Types.choices,
                            default=Types.ADMIN)

    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    
    def save(self, *args, **kwargs):
        if not self.pk:   
            self.type = self.base_type
            return super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username:": self.username})

class ElderManager(models.Manager):
    def get_queryset(slef, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.ELDER)

class RelatedManager(models.Manager):
    def get_queryset(slef, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.ELDER_RELATED)

class Socail_workerManager(models.Manager):
    def get_queryset(slef, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.SOCIAL_WORKER)


class Elder(User):
    base_type = User.Types.ELDER
    objects = ElderManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = User.Types.ELDER
        return super().save(*args, **kwargs)
    
class Related(User):
    objects = RelatedManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = User.Types.ELDER_RELATED
        return super().save(*args, **kwargs)

class Social_worker(User):
    objects = Socail_workerManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = User.Types.SOCIAL_WORKER
        return super().save(*args, **kwargs)

'''
class Elder_Related(User):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
'''