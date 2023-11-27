from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.dispatch import receiver
from django.utils import timezone
import os
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

def upload_profile(instance, filename):
    userid = instance.username
    filename = userid +".jpg"
    # Get the path to the upload directory
    upload_dir = os.path.join("Profile", userid)

    # If a file with this name already exists, delete it
    existing_file_path = os.path.join(upload_dir)
    existing_file_path = str(existing_file_path) + "/"
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
    upload_profile = models.FileField(upload_to=upload_profile, null=True, blank=True, default=None, storage=OverwriteStorage())
    
    def save(self, *args, **kwargs):
        print(upload_profile)
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
    uploader = instance.uploader
    uploadername = uploader.username

    current_datetime = datetime.now().strftime('%Y%m%d%H%M%S')  # Get current datetime as a string

    # Get the names of all tagged elders and join them with underscores
    tagged_elders = '_'.join([elder.username for elder in instance.taggedElder.all()])

    # Combine the filename with the datetime, tagged elders, and file extension
    new_filename = f"{current_datetime}_{tagged_elders}_{filename}"

    return os.path.join("Elder Media Record", uploadername, new_filename)

class ElderRecord(models.Model):
    DatetimeOfUpload = models.DateTimeField(auto_now=True)
    taggedElder = models.ManyToManyField(User, related_name='taggedElder')
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='records_uploader')
    uploadedFile = models.FileField(upload_to=media_upload_path)

    def __str__(self):
        return self.uploadedFile.name

class Questionnaire(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    assigned_to = models.ManyToManyField(User, related_name='assigned_questionnaires', limit_choices_to={'type__in': [User.Types.ADMIN, User.Types.MANAGER]})
    assigned_at = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField()

    def __str__(self):
        return self.title

class Question(models.Model):
    TEXT = 'text'
    AUDIO = 'audio'
    VIDEO = 'video'
    
    QUESTION_TYPE_CHOICES = [
        (TEXT, 'Text'),
        (AUDIO, 'Audio'),
        (VIDEO, 'Video'),
    ]

    text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES, default=TEXT)
    multimedia_content = models.FileField(upload_to='question_multimedia/', blank=True, null=True)

    def __str__(self):
        return self.text 


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    response_text = models.TextField(blank=True, null=True)
    response_audio = models.FileField(upload_to='answer_audio/', blank=True, null=True)
    response_video = models.FileField(upload_to='answer_video/', blank=True, null=True)
    submitted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.questionnaire.title} - {self.question.text}"
 