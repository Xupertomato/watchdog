from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.
class User(AbstractUser):
    
    class Types(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        ELDER = "ELDER", "Elder"
        RELATED = "RELATED", "Related"
        MANAGER= "MANAGER", "Manager"
    
    base_type = Types.ADMIN

    type = models.CharField(_("Type"), 
                            max_length=50, 
                            choices=Types.choices,
                            default=Types.ADMIN)
    id_card = models.CharField(max_length=255, verbose_name="ID card number")
    
    def save(self, *args, **kwargs):
        if not self.pk:   
            self.type = self.base_type
            return super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"id_card:": self.id_card})

class ElderManager(models.Manager):
    def get_queryset(slef, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.ELDER)

class RelatedManager(models.Manager):
    def get_queryset(slef, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.RELATED)

class Manager_Manager(models.Manager):
    def get_queryset(slef, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.MANAGER)


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
    base_type = User.Types.RELATED    
    objects = RelatedManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = User.Types.RELATED
        return super().save(*args, **kwargs)

class Manager(User):
    objects = Manager_Manager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = User.Types.MANAGER
        return super().save(*args, **kwargs)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # 性別，預設為男性
    class SexTypes(models.TextChoices):
        MALE = "MALE", "男"
        FEMALE = "FEMALE", "女"
        ELSE = "ELSE", "其他"

    base_type = SexTypes.MALE
    sex = models.CharField(
        max_length=10, choices=SexTypes.choices, default=base_type, verbose_name="sex"
    )
    
    
    # 姓名
    l_name = models.CharField(max_length=8, verbose_name="last name")
    f_name = models.CharField(max_length=8, verbose_name="first name")
    # 手機號碼
    phone_num = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r"^09\d{8}$", message="手機號碼格式輸入錯誤！")],
        verbose_name="phone number",
    )
    address = models.CharField(max_length=255, verbose_name="address")
    birthday = models.DateField(verbose_name="birthday")
    
    """Related and Manager"""
    line_id = models.CharField(max_length=255, verbose_name="line id")
    
    


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, "profile"):
        Profile.objects.create(user=instance)
    instance.profile.save()