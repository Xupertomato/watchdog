from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Profile, User, Profile
from datetime import date, timedelta

User = get_user_model()

profile_common_fields = ["f_name","l_name", "birthday", "sex", "phone_num", "address"]

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["id_card", "password1", "password2"]
        
class LoginForm(AuthenticationForm):
    id_card = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "帳號"}))
    password = forms.PasswordInput()

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                _("This account is inactive."),
                code="inactive",
            )

class ElderForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = profile_common_fields

class RelatedForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = profile_common_fields

class ManagerForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = profile_common_fields