from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.timezone import now
from django.views import generic
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth import get_user, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib.auth import logout # 匯入logout函式
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from datetime import date
from .models import *
from .forms import *

class SignUpAndLoginView(TemplateView):
    template_name = "app/signup_and_login.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
        if self.user_type == User.Types.ELDER:
            self.ProfileForm = ElderForm
        elif self.user_type == User.Types.RELATED:
            self.ProfileForm = RelatedForm
        else:
            self.ProfileForm = ManagerForm

    def get(self, request):
        signup_form = SignUpForm()
        login_form = LoginForm()
        profile_form = self.ProfileForm()

        return render(
            request,
            self.template_name,
            {
                "signup_form": signup_form,
                "profile_form": profile_form,
                "login_form": login_form,
            },
        )

    def post(self, request):
        signup_form = SignUpForm(request.POST)
        profile_form = self.ProfileForm(request.POST)
        login_form = LoginForm(data=request.POST)

        if login_form.is_valid():
            login(self.request, login_form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            return redirect(reverse("app:carpools"))

        error = None
        login_error = None
        
        return render(
            request,
            self.template_name,
            {
                "signup_form": signup_form,
                "profile_form": profile_form,
                "login_form": login_form,
                "messages": messages,
                "error": error,
                "login_error": login_error,
            },
        )


class ElderSignUpAndLoginView(SignUpAndLoginView):
    def __init__(self):
        super().__init__(user_type=User.Types.ELDER)


class RelatedSignUpAndLoginView(SignUpAndLoginView):
    def __init__(self):
        super().__init__(user_type=User.Types.RELATED)
        
class ManagerSignUpAndLoginView(SignUpAndLoginView):
    def __init__(self):
        super().__init__(user_type=User.Types.MANAGER)
        
def logout_view(request): # 呼叫logout函式，它會把request當作引數，然後重新導向主頁
    logout(request)
    return HttpResponseRedirect(reverse('watchdogApp:index'))

def register_base(request):
    
    return render(request, 'users/register_base.html')
    
def register＿related(request):
    """Register a new user."""
    if request.method != 'POST':  
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)
        
        if form.is_valid():
            new_user = form.save()
            authenticated_user = authenticate(username=new_user.username,password=request.POST['password1'])
            login(request, authenticated_user)
            return HttpResponseRedirect(reverse('watchdogApp:index'))

    context = {'form': form}
    return render(request, 'users/register_related.html', context)

def register＿elder(request):
    """Register a new user."""
    if request.method != 'POST':  
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)
        
        if form.is_valid():
            new_user = form.save()
            authenticated_user = authenticate(username=new_user.username,password=request.POST['password1'])
            login(request, authenticated_user)
            return HttpResponseRedirect(reverse('watchdogApp:index'))

    context = {'form': form}
    return render(request, 'users/register_elder.html', context)

def register＿manager(request):
    """Register a new user."""
    if request.method != 'POST':  
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)
        
        if form.is_valid():
            new_user = form.save()
            authenticated_user = authenticate(username=new_user.username,password=request.POST['password1'])
            login(request, authenticated_user)
            return HttpResponseRedirect(reverse('watchdogApp:index'))

    context = {'form': form}
    return render(request, 'users/register_manager.html', context)