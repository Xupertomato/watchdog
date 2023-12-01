from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm, UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from django.views.generic import CreateView
from django.contrib.auth import logout
from .models import *
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import PermissionRequiredMixin
from .forms import *
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.views.generic import DetailView


def index(request):
  context = {
    'segment': 'index'
  }
  return render(request, "pages/index.html", context)

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
    'segment': 'elder_data'
  }
  return render(request, 'pages/elder_data.html', context)


#問卷相關
def add_questionnaire_view(request):
    if request.method == 'POST':
        form = QuestionnaireForm(request.POST)
        if form.is_valid():
            questionnaire = form.save()
            return redirect('questionnaire_list')
    else:
        form = QuestionnaireForm()

    return render(request, 'pages/add_questionnaire.html', {'form': form})
    return render(request, 'pages/add_questionnaire.html', {'form': form})      


def questionnaire_list_view(request):
    questionnaires = Questionnaire.objects.all()
    return render(request, 'pages/questionnaire_list.html', {'questionnaires': questionnaires})
  
@login_required(login_url='/accounts/login/')
def answer_page_view(request, pk):
    questionnaire = get_object_or_404(Questionnaire, pk=pk)
    questions = questionnaire.question_set.all()  # Corrected this line

    if request.method == 'POST':
        form = AnswerForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the answers
            for question in questions:
                Answer.objects.create(
                    user=request.user,
                    questionnaire=questionnaire,
                    question=question,
                    response_text=form.cleaned_data.get(f'response_text_{question.id}'),
                    response_audio=form.cleaned_data.get(f'response_audio_{question.id}'),
                    response_video=form.cleaned_data.get(f'response_video_{question.id}'),
                )
            return render(request, 'pages/success_page.html')  # Customize this page as needed
    else:
        form = AnswerForm()

    return render(request, 'pages/answer_page.html', {'questionnaire': questionnaire, 'questions': questions, 'form': form})

def edit_questionnaire_view(request, pk):
    questionnaire = get_object_or_404(Questionnaire, pk=pk)

    if request.method == 'POST':
        form = QuestionnaireForm(request.POST, instance=questionnaire)
        if form.is_valid():
            form.save()
            # Redirect to the questionnaire list or any other page after saving
            return redirect('questionnaire_list')
    else:
        form = QuestionnaireForm(instance=questionnaire)

    return render(request, 'pages/edit_questionnaire.html', {'form': form})

def delete_questionnaire_view(request, pk):
    questionnaire = get_object_or_404(Questionnaire, pk=pk)

    if request.method == 'POST':
        questionnaire.delete()
        # Redirect to the questionnaire list or any other page after deletion
        return redirect('questionnaire_list')

    return render(request, 'pages/delete_questionnaire_confirm.html', {'questionnaire': questionnaire})
  
  
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
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.type = User.Types.ELDER
        self.object.save()
        
        related_users = form.cleaned_data['related_users']
        user_relationship = UserRelationship.objects.create()
        user_relationship.elders.add(self.object)
        user_relationship.managers.add(*related_users)
        
        return super().form_valid(form)

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
def profile_page(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'pages/profile.html', {'user': user})

@login_required(login_url='/accounts/login/')
def edit_profile(request, username):
    if request.method == 'POST':
        user = get_object_or_404(User, username=username)  # noqa: F405
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'成功更新個人資料！')
            return redirect('profile')
            
    else:
        form = UserUpdateForm(instance=request.user)

    context = {'form': form}
    return render(request, 'pages/profile_edit.html', context)

class ElderRecordUploadView(FormView):
  template_name='add_record.html'
  form_class = ElderRecordForm  
  success_url = 'forms/upload_elder_record/'
  
  @login_required(login_url='/accounts/login/')
  def upload_elder_record(request):
      if request.method == 'POST':
          form = ElderRecordForm(request.POST, request.FILES, request=request)
          if form.is_valid():
              form.save()
              messages.success(request, '成功上傳！')
              return redirect('/forms/upload_elder_record/')
          else:
              messages.error(request, '上傳失敗！')
                
      else:
          form = ElderRecordForm()
          
      users = User.objects.filter(type='ELDER')
      return render(request, 'pages/add_record.html', {'form': form, 'users': users})
    
    
class ElderRecordViewView(LoginRequiredMixin, ListView):
  model = ElderRecord
  template_name = 'pages/elder_record.html'
  context_object_name = 'records'
  
  def get_queryset(self):
    # Filter the records based on the current user's tagged elders
    return super().get_queryset().filter(taggedElder=self.request.user)
  
class ElderListView(LoginRequiredMixin, ListView):
    model = UserRelationship
    template_name = 'pages/elder_list.html'
    context_object_name = 'relationship'
    
    def get_queryset(self):
      manager_relationships = UserRelationship.objects.filter(managers=self.request.user)
      
      # Create an empty list to store all the elders managed by the user
      elders_managed = []

      for relationship in manager_relationships:
          elders_managed.extend(relationship.elders.all())

      return elders_managed
          
@method_decorator(login_required, name='dispatch')
class ElderRecordDetailView(DetailView):
    model = ElderRecord
    template_name = 'elder_record.html'
    context_object_name = 'record'

    def get_queryset(self):
        # Filter the records based on the current user's tagged elders
        return super().get_queryset().filter(taggedElder=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        # Check if the requesting user is a manager with a relationship to the elder
        record = self.get_object()
        elder = record.taggedElder.first()  # Assuming an elder is always associated with a record

        if elder and request.user in elder.managers.all():
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404("您沒有權限瀏覽此頁面！")

################################################################
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