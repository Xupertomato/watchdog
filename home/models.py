from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
import os

class User(AbstractUser):
    class Types(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MANAGER = 'MANAGER', '管理員'
        ELDER = 'ELDER', '長者'
        
    base_type = Types.ELDER  
    type = models.CharField(_("Type"), 
                            max_length=50, 
                            choices=Types.choices,
                            default=Types.MANAGER)
    
    # 姓名
    name = models.CharField(max_length=8, verbose_name="name", default="")
    
    class SexTypes(models.TextChoices):
        MALE = "MALE", "男"
        FEMALE = "FEMALE", "女"
        ELSE = "ELSE", "其他"

    base_sex_type = SexTypes.MALE
    sex = models.CharField(
        max_length=10, choices=SexTypes.choices, default=base_sex_type, verbose_name="sex"
    )
    
    birthday = models.DateField(verbose_name="birthday", default=timezone.localdate)
    
    # 手機號碼
    phone_num = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r"^09\d{8}$", message="手機號碼格式輸入錯誤！")],
        verbose_name="phone_num",
        default=""
    )
    address = models.CharField(max_length=255, verbose_name="address", default="")
    
    def save(self, *args, **kwargs):
        if not self.pk:   
            self.type = self.base_type
            return super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

class ElderManager(models.Manager):
    def get_queryset(slef, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.ELDER)

class Manager_Manager(models.Manager):
    def get_queryset(slef, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.MANAGER)

class Elder(User):
    objects = ElderManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = User.Types.ELDER
        return super().save(*args, **kwargs)

class Manager(User):
    objects = Manager_Manager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = User.Types.MANAGER
        return super().save(*args, **kwargs)

def get_upload_path(instance, filename):
    user = instance.uploader
    username = user.username
    return os.path.join("Uploaded Files", username, filename)

class ElderRecord(models.Model):
    dateTimeOfUpload = models.DateTimeField(auto_now = True)
    user_tag = models.ManyToManyField(User, related_name='user_tag')
    uploader = models.OneToOneField(User, on_delete=models.CASCADE)
    uploadedFile = models.FileField(upload_to=get_upload_path)
    
