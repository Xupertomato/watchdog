from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm, UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from django.views.generic import CreateView
from django.contrib.auth import logout
from .models import *
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from .forms import *
from django.views.generic.edit import CreateView
from django.contrib import messages

def index(request):
  context = {
    'segment': 'index'
  }
  return render(request, "pages/index.html", context)

# Components
@login_required(login_url='/accounts/login/')
def bc_button(request):
  context = {
    'parent': 'basic_components',
    'segment': 'button'
  }
  return render(request, "pages/components/bc_button.html", context)

@login_required(login_url='/accounts/login/')
def bc_badges(request):
  context = {
    'parent': 'basic_components',
    'segment': 'badges'
  }
  return render(request, "pages/components/bc_badges.html", context)

@login_required(login_url='/accounts/login/')
def bc_breadcrumb_pagination(request):
  context = {
    'parent': 'basic_components',
    'segment': 'breadcrumbs_&_pagination'
  }
  return render(request, "pages/components/bc_breadcrumb-pagination.html", context)

@login_required(login_url='/accounts/login/')
def bc_collapse(request):
  context = {
    'parent': 'basic_components',
    'segment': 'collapse'
  }
  return render(request, "pages/components/bc_collapse.html", context)

@login_required(login_url='/accounts/login/')
def bc_tabs(request):
  context = {
    'parent': 'basic_components',
    'segment': 'navs_&_tabs'
  }
  return render(request, "pages/components/bc_tabs.html", context)

@login_required(login_url='/accounts/login/')
def bc_typography(request):
  context = {
    'parent': 'basic_components',
    'segment': 'typography'
  }
  return render(request, "pages/components/bc_typography.html", context)

@login_required(login_url='/accounts/login/')
def icon_feather(request):
  context = {
    'parent': 'basic_components',
    'segment': 'feather_icon'
  }
  return render(request, "pages/components/icon-feather.html", context)


# Forms and Tables
@login_required(login_url='/accounts/login/')
def add_users(request):
  context = {
    'parent': 'form_components',
    'segment': 'add_users'
  }
  return render(request, 'pages/add_users.html', context)

@login_required(login_url='/accounts/login/')
def basic_tables(request):
  context = {
    'parent': 'tables',
    'segment': 'basic_tables'
  }
  return render(request, 'pages/tbl_bootstrap.html', context)

# Chart and Maps
@login_required(login_url='/accounts/login/')
def morris_chart(request):
  context = {
    'parent': 'chart',
    'segment': 'morris_chart'
  }
  return render(request, 'pages/chart-morris.html', context)

@login_required(login_url='/accounts/login/')
def google_maps(request):
  context = {
    'parent': 'maps',
    'segment': 'google_maps'
  }
  return render(request, 'pages/map-google.html', context)

# #Permissions
# class AdminManagerPermission(PermissionRequiredMixin):
#     def has_permission(self):
#         user = self.request.user
#         if user.is_authenticated and user.type in ['ADMIN', 'MANAGER']:
#             return True
#         return False
      
# Authentication
class UserRegistrationView(CreateView):
  template_name = 'accounts/auth-signup.html'
  form_class = RegistrationForm
  success_url = '/accounts/register/'

class ElderRegistrationView(PermissionRequiredMixin, CreateView):
    template_name = 'accounts/elder-signup.html'
    form_class = ElderRegistrationForm
    success_url = '/accounts/elder-register/'
    permission_required = 'home.can_view_elder_registration'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def has_permission(self):
        user = self.request.user
        return super().has_permission() or (user.is_authenticated and user.type == 'MANAGER')

class UserLoginView(LoginView):
  template_name = 'accounts/auth-signin.html'
  form_class = LoginForm

class UserPasswordResetView(PasswordResetView):
  template_name = 'accounts/auth-reset-password.html'
  form_class = UserPasswordResetForm

class UserPasswrodResetConfirmView(PasswordResetConfirmView):
  template_name = 'accounts/auth-password-reset-confirm.html'
  form_class = UserSetPasswordForm

class UserPasswordChangeView(PasswordChangeView):
  template_name = 'accounts/auth-change-password.html'
  form_class = UserPasswordChangeForm

def logout_view(request):
  logout(request)
  return redirect('/')


@login_required(login_url='/accounts/login/')
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)

    context = {'form': form}
    return render(request, 'pages/profile.html', context)
  
@login_required(login_url='/accounts/login/')
def upload_elder_record(request):
    if request.method == 'POST':
        form = ElderRecordForm(request.POST, request.FILES)
        if form.is_valid():
            uploader = request.user
            elder_record, created = ElderRecord.objects.get_or_create(uploader=uploader)
            elder_record.uploadedFile = form.cleaned_data['uploadedFile']
            elder_record.user_tag.set(form.cleaned_data['user_tag'])
            elder_record.save()
            return redirect('/forms/upload_elder_record/')
    else:
        form = ElderRecordForm()
    users = User.objects.all()
    return render(request, 'pages/add_record.html', {'form': form, 'current_user': request.user, 'users': users})