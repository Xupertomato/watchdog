from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm, UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from django.views.generic import CreateView
from django.contrib.auth import logout
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.views.generic import DetailView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.conf import settings
from django.http import HttpResponseRedirect
from google.auth.transport.requests import Request
from httplib2 import Http
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from django.http import HttpResponse



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

@user_passes_test(lambda u: u.is_superuser, login_url='/accounts/login/')  
def redirect_to_google_oauth(request):
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_FORM_CLIENT_SECRETS_PATH,
        scopes=[settings.SCOPES],
        redirect_uri=request.build_absolute_uri('/oauth2callback/')
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    # Store the state in the session for later use
    request.session['state'] = state

    return redirect(authorization_url)
  
def oauth2callback(request):
    state = request.session.get('state')


    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_FORM_CLIENT_SECRETS_PATH,
        scopes=settings.SCOPES,
        state=state,
        redirect_uri=request.build_absolute_uri('/oauth2callback/')
    )

    try:
        # Fetch token with the correct scopes
        flow.fetch_token(authorization_response=request.build_absolute_uri())

        credentials = flow.credentials
        # Save credentials with both scopes
        with open(settings.GOOGLE_FORM_TOKEN_PATH, 'w') as token_file:
            token_file.write(credentials.to_json())

        return redirect('questionnaire_list')
    except Exception as e:
        print(f"Error during OAuth callback: {e}")
        return HttpResponse("An error occurred during authentication.", status=500)

 
  
@user_passes_test(lambda u: u.is_superuser, login_url='/accounts/login/')
def add_questionnaire_view(request):
    if request.method == 'POST':
        questionnaire_form = QuestionnaireForm(request.POST)
        answer_form = AnswerForm(request.POST)

        if questionnaire_form.is_valid():
            form_url = questionnaire_form.cleaned_data.get('edit_url')

        if not os.path.exists(settings.GOOGLE_FORM_TOKEN_PATH):
          return redirect('google_oauth')

        form_data = get_form_data(form_url)
        
        if form_data:
            questionnaire = questionnaire_form.save(commit=False)
            questionnaire.title = form_data.get('title')
            questionnaire.description = form_data.get('description')
            questionnaire.edit_url = form_url
            questionnaire.save()

            if answer_form.is_valid():
              # Populate answer form with the required data
              answer = Answer.objects.get(questionnaire=questionnaire)
              answer.questions = form_data.get('questions')
              answer.save()

        return redirect('questionnaire_list')      
          
    else:
      questionnaire_form = QuestionnaireForm()
      answer_form = AnswerForm()

    return render(request, 'pages/add_questionnaire.html', {'questionnaire_form': questionnaire_form, 'answer_form': answer_form})

def get_form_data(form_url):
    try:
        # Load credentials from the file
        with open(settings.GOOGLE_FORM_TOKEN_PATH, 'r') as token_file:
            token_info = json.load(token_file)
            creds = Credentials.from_authorized_user_info(token_info)

        # Refresh the credentials if they are expired
        if creds.expired:
            creds.refresh(Request())
            with open(settings.GOOGLE_FORM_TOKEN_PATH, 'w') as token_file:
                token_file.write(creds.to_json())

    except FileNotFoundError:
        print("No credentials found. Need to authenticate first.")
        return None
    except KeyError:
        print("Error loading credentials. File format may be incorrect.")
        return None

    # Create a Google Forms service client using the credentials
    service = build('forms', 'v1', credentials=creds)

    try:
        # Extract the form ID from the URL and use it to fetch the form data
        form_id = form_url.split("/")[-2]
        form = service.forms().get(formId=form_id).execute()
        
        questions = {}
        for item in form.get('items', []):
            title = item.get('title')
            question_id = item.get('questionItem', {}).get('question', {}).get('questionId')

            if title and question_id:
                questions[question_id] = title
        
        return {
            'title': form.get('info', {}).get('title'),
            'description': form.get('info', {}).get('description'),
            'questions': questions
        }


    except Exception as e:
        print(f"Error retrieving form data: {e}")
        return None


@user_passes_test(lambda u: u.is_superuser, login_url='/accounts/login/')       
def update_response_view(request):

    if not os.path.exists(settings.GOOGLE_FORM_TOKEN_PATH):
          return redirect('google_oauth')
        
    form_id = request.GET.get('form_id', '')
    print(form_id)
    if not form_id:
        # Handle the case where form_id is not provided
        return redirect('questionnaire_list')
      
    try:
      # Load credentials from the file
      with open(settings.GOOGLE_FORM_TOKEN_PATH, 'r') as token_file:
          token_info = json.load(token_file)
          creds = Credentials.from_authorized_user_info(token_info)

      # Refresh the credentials if they are expired
      if creds.expired:
          creds.refresh(Request())
          with open(settings.GOOGLE_FORM_TOKEN_PATH, 'w') as token_file:
              token_file.write(creds.to_json())

    except FileNotFoundError:
      print("No credentials found. Need to authenticate first.")
      return None
    except KeyError:
      print("Error loading credentials. File format may be incorrect.")
      return None

    # Create a Google Forms service client using the credentials
    service = build('forms', 'v1', credentials=creds)
    
    try:
      # Extract the form ID from the URL and use it to fetch the form data
      responses = service.forms().responses().list(formId=form_id).execute()
      print(responses)
      questionnaire = Questionnaire.objects.get(edit_url__contains=form_id)
      answer = Answer.objects.get(questionnaire=questionnaire)
      answer.response_data = responses
      answer.save()  

    except Exception as e:
        print(f"Error retrieving form data: {e}")
        return None

    return render(request, 'pages/questionnaire_list.html')

 
def process_form_responses(questionnaire_id, responses):
  # Retrieve all usernames from the User model
  usernames = set(User.objects.values_list('username', flat=True))

  # Retrieve the Questionnaire and its related Answer object
  answer = Answer.objects.get(questionnaire_id=questionnaire_id)

  # Find the question ID for the username question
  username_question_id = next((key for key, value in answer.questions.items() if value == "username"), None)
  if not username_question_id:
      print("Username question ID not found.")
      return
    
  # Process each response
  for response in responses:
      # Extract the response data
      response_data = response.get('answers', {})

      # Check if the username exists in the database
      username_response = response_data.get(username_question_id, {}).get('textAnswers', {}).get('answers', [{}])[0].get('value', '')
      
      if username_response in usernames:
          # Process and save valid responses
          mapped_response = {}
          for question_id, title in answer.response_data.items():
              question_response = response_data.get(question_id, {}).get('textAnswers', {}).get('answers', [{}])[0].get('value', '')
              mapped_response[title] = question_response 


@login_required(login_url='/accounts/login/')
def questionnaire_list_view(request):
    questionnaires = Questionnaire.objects.all()
    return render(request, 'pages/questionnaire_list.html', {'questionnaires': questionnaires})

@login_required(login_url='/accounts/login/')
def edit_questionnaire_view(request, pk):
    questionnaire = get_object_or_404(Questionnaire, pk=pk)

    if request.method == 'POST':
        form = QuestionnaireForm(request.POST, instance=questionnaire)
        if form.is_valid():
            # Save Questionnaire without nested objects
            questionnaire = form.save(commit=False)
            question_formset = form.cleaned_data['question_formset']
            # Delete flagged questions
            for form in question_formset:
                if form.cleaned_data['is_deleted']:
                    form.instance.delete()
            # Save remaining questions
            question_formset.save()
            form.save()
            messages.success(request, "Questionnaire updated successfully!")
            return redirect('questionnaire_list')
    else:
        form = QuestionnaireForm(instance=questionnaire)

    context = {'form': form}
    return render(request, 'pages/edit_questionnaire.html', context)

def delete_questionnaire_view(request, pk):
    questionnaire = get_object_or_404(Questionnaire, pk=pk)

    if request.method == 'POST':
        questionnaire.delete()
        # Redirect to the questionnaire list or any other page after deletion
        return redirect('questionnaire_list')

    return render(request, 'pages/delete_questionnaire_confirm.html', {'questionnaire': questionnaire})

@user_passes_test(lambda u: u.is_superuser, login_url='/accounts/login/') 
def answer_list_view(request, pk):
    questionnaire = get_object_or_404(Questionnaire, pk=pk)
    answers = Answer.objects.filter(questionnaire=questionnaire)  # Fetch answers for this questionnaire
    return render(request, 'pages/answer_list.html', {'answers': answers, 'questionnaire': questionnaire})  
  
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

@csrf_exempt  # Disable CSRF for this view
@require_http_methods(["POST"])  # Only allow POST requests
def handle_google_form_response(request):
    data = json.loads(request.body)  # Assuming data is sent as JSON

    # Extract the username and questionnaire information
    username = data.get('username')  # Replace 'username' with the actual key used in your JSON
    questionnaire_id = data.get('questionnaire_id')  # Replace with the actual key

    # Check if the user exists in the database
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        # Handle the case where the user does not exist
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

    # Check if the questionnaire exists
    try:
        questionnaire = Questionnaire.objects.get(id=questionnaire_id)
    except Questionnaire.DoesNotExist:
        # Handle the case where the questionnaire does not exist
        return JsonResponse({'status': 'error', 'message': 'Questionnaire not found'}, status=404)

    # Process the rest of the data and create/update the Answer object
    # ...

    return JsonResponse({'status': 'success'})



  
  
  
  
  

