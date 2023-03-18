from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, UsernameField, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import *


class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(
      label=_("Password"),
      widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '輸入密碼'}),
        )
    password2 = forms.CharField(
      label=_("Confirm Password"),
      widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '請再次輸入密碼'}),
        )     
    type = forms.ChoiceField(
        choices=[(choice[0], choice[1]) for choice in User.Types.choices if choice[0] != 'ADMIN'],
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': '身份'}),
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', "name", "sex", "type", "phone_num", "birthday", "address")
        
        widgets = {
        'username': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '身分證字號'
        }),
        'email': forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        }),
        'name': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '名字'
        }),
        'sex': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': '性別'
        }),
        'type': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': '身份'
        }),
        'phone_num': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '電話'
        }),
        'birthday': forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': '出生日期'
        }),
        'address': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '地址'
        })
        }

class ElderRegistrationForm(UserCreationForm):
    password1 = forms.CharField(
      label=_("Password"),
      widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '輸入密碼'}),
  )
    password2 = forms.CharField(
      label=_("Confirm Password"),
      widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '請再次輸入密碼'}),
  )
         
    class Meta:
        model = User
        fields = ('username', 'email', "name", "sex", "phone_num", "birthday", "address")
        
        widgets = {
        'username': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '身分證字號'
        }),
        'name': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '名字'
        }),
        'email': forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        }),
        'sex': forms.Select(choices=(('男', 'MALE'), ('女', 'FEMALE'), ("其他", 'ELSE')), attrs={
                'class': 'form-control',
                'placeholder': '性別'
        }),
        'phone_num': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '電話'
        }),
        'birthday': forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': '出生日期'
        }),
        'address': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '地址'
        })
        }

class LoginForm(AuthenticationForm):
  username = UsernameField(label=_("Your Username"), widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "身分證字號"}))
  password = forms.CharField(
      label=_("Your Password"),
      strip=False,
      widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
  )

class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))

class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'New Password'
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirm New Password'
    }), label="Confirm New Password")
    

class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Old Password'
    }), label='Old Password')
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'New Password'
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirm New Password'
    }), label="Confirm New Password")


class ElderRecordForm(forms.ModelForm):
    class Meta:
        model = ElderRecord
        fields = ['user_tag', 'uploadedFile']
        widgets = {
            'user_tag': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # save request object as instance attribute
        super(ElderRecordForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        elder_record = super(ElderRecordForm, self).save(commit=False)
        if commit:
            elder_record.uploader = self.request.user  # set uploader as current user
            elder_record.save()
            self.save_m2m()
        return elder_record


    