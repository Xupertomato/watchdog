from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.dispatch import receiver
from django.utils import timezone
import os,datetime


def upload_profile(instance, filename):
    userid = instance.username
    filename = userid +".jpg"
    # Get the path to the upload directory
    upload_dir = os.path.join("Profile", userid)

    # If a file with this name already exists, delete it
    existing_file_path = os.path.join(upload_dir)
    existing_file_path = str(existing_file_path) + "/"
    print(os.path.isfile(existing_file_path))
    print(existing_file_path)
    if os.path.isfile(existing_file_path):
        print("Deleting existing")
        os.remove(existing_file_path)

    # Return the original filename to save the new file with that name
    return os.path.join("Profile", userid, filename)

class User(AbstractUser):
    class Types(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MANAGER = 'MANAGER', '管理員'
        ELDER = 'ELDER', '長者'
        
    base_type = Types.ADMIN  
    type = models.CharField(_("Type"), 
                            max_length=50, 
                            choices=Types.choices,
                            default=base_type)
    
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
    
    birthday = models.DateField(verbose_name="birthday")
    
    # 手機號碼
    phone_num = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r"^09\d{8}$", message="手機號碼格式輸入錯誤！")],
        verbose_name="phone_num",
        default=""
    )
    address = models.CharField(max_length=255, verbose_name="address", default="")
    
    #使用者照片路徑
    upload_profile = models.FileField(upload_to=upload_profile, null=True, blank=True, default=None)
    
    def save(self, *args, **kwargs):
        self.type = self.type
        return super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})
    
    
    
class UserRelationship(models.Model):
    elders = models.ManyToManyField(User, related_name='managers', limit_choices_to={'type': User.Types.ELDER})
    managers = models.ManyToManyField(User, related_name='elders', limit_choices_to={'type': User.Types.MANAGER})

class ElderManager(models.Manager):
    def get_queryset(slef, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.ELDER)
    
    def normalize_email(self, email):
        # do nothing
        return email

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

def media_upload_path(instance, filename):
    user = instance.uploader
    username = user.username
    return os.path.join("Elder Media Record", username, filename)

class ElderRecord(models.Model):
    DatetimeOfUpload = models.DateTimeField(auto_now=True)
    taggedElder = models.ManyToManyField(User, related_name='taggedElder')
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='records_uploader')
    uploadedFile = models.FileField(upload_to=media_upload_path)

    def __str__(self):
        return self.uploadedFile.name

    