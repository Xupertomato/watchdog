from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, UsernameField, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import *
from multiupload.fields import MultiFileField, MultiMediaField
from django.core.files.uploadedfile import InMemoryUploadedFile
import io
from django.forms import formset_factory

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
        fields = ('username', 'name', 'email', 'sex', 'type', 'phone_num', 'birthday', 'address', 'upload_profile')
            
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
            }),
            'upload_profile': forms.FileInput(attrs={
                'class': 'form-control',
                'placeholder': '使用者圖片'
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
    related_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(type__in=[User.Types.ADMIN, User.Types.MANAGER]),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Related users"
    )      
    class Meta:
        model = Elder
        fields = ('username', "name", "sex", "phone_num", "birthday", "address", 'upload_profile', "related_users")
        
        widgets = {
        'username': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '身分證字號'
        }),
        'name': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '名字'
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
        }),
        'upload_profile': forms.FileInput(attrs={
                'class': 'form-control',
                'placeholder': '使用者圖片'
        })
        }


class LoginForm(AuthenticationForm):
  username = UsernameField(label=_("你的名字"), widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "身分證字號"}))
  password = forms.CharField(
      label=_("你的密碼"),
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
        'class': 'form-control', 'placeholder': '新密碼'
    }), label="新密碼")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': '再次確認新密碼'
    }), label="再次確認新密碼")
    

class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': '舊密碼'
    }), label='舊密碼')
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': '新密碼'
    }), label="新密碼")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': '再次確認新密碼'
    }), label="再次確認新密碼")

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'sex', 'phone_num', 'birthday', 'address', "upload_profile"]
        widgets = {
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
        'birthday': forms.DateInput(format=('%Y-%m-%d'),attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        'address': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '地址'
        }),
        'upload_profile': forms.FileInput(attrs={
                'class': 'form-control',
                'placeholder': '使用者圖片'
        })
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    
class ElderRecordForm(forms.ModelForm):
    class Meta:
        model = ElderRecord  
        fields = ['taggedElder']
        widgets = {
            'taggedElder': forms.CheckboxSelectMultiple(),
        }
        
    uploadedFile = MultiMediaField(
        min_num=1,
        max_num=10,
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # save request object as instance attribute
        super(ElderRecordForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        elder_records = []
        for uploaded_file in self.cleaned_data['uploadedFile']:
            elder_record = super().save(commit=False)
            elder_record.uploader = self.request.user
            elder_record.save()  # Save the elder_record instance to generate the ID
            elder_record.uploadedFile.save(uploaded_file.name, uploaded_file)
            elder_record.taggedElder.set(self.cleaned_data['taggedElder'])  # Set the many-to-many relationship
            if commit:
                elder_record.save()
            elder_records.append(elder_record)
        return elder_records

class QuestionnaireForm(forms.ModelForm):

    class Meta:
        model = Questionnaire
        fields = ['edit_url', 'reply_url', 'assigned_by', 'assigned_at']
        widgets = {
            'edit_url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '編輯問卷網址'}),
            'reply_url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '回覆問卷網址'}),
            'assigned_by': forms.Select(attrs={'class': 'form-control'}),
            'assigned_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(QuestionnaireForm, self).__init__(*args, **kwargs)
        self.fields['assigned_by'].queryset = User.objects.filter(is_superuser=True)

    def clean_edit_url(self):
        edit_url = self.cleaned_data.get("edit_url")
        if not edit_url.endswith("edit"):
            raise ValidationError("URL must end with 'edit'.")
        return edit_url

    def clean_reply_url(self):
        reply_url = self.cleaned_data.get("reply_url")
        if "usp=pp_url&entry" not in reply_url:
            raise ValidationError("URL must contain 'usp=pp_url&entry'.")

        # Remove only the part after the last '='
        parts = reply_url.rsplit('=', 1)
        if len(parts) > 1:
            reply_url = parts[0]

        return reply_url



class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['questions','response_data']
        
    