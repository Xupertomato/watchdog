from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Carfare, Profile, Carpool, Comment, Car, User, Profile
from datetime import date, timedelta

User = get_user_model()

