from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import *


urlpatterns = [
  path('', views.index, name='index'),

  # Elder
  path('forms/upload_elder_record/', views.ElderRecordUploadView.upload_elder_record, name='add_record'),
  path('tables/elder_record/', ElderRecordViewView.as_view(), name='elder_record'),
  path('elder-list/', ElderListView.as_view(), name='elder_list'),
  path('accounts/elder-register/', views.ElderRegistrationView.as_view(), name='elder_register'),
  path('search/', views.elder_search_view, name='elder_search_view'),  

  # Authentication
  path('accounts/register/', views.UserRegistrationView.as_view(), name='register'),
  path('accounts/login/', views.UserLoginView.as_view(), name='login'),
  path('accounts/logout/', views.logout_view, name='logout'),
  path('accounts/password-change/', views.UserPasswordChangeView.as_view(), name='password_change'),
  path('accounts/password-change-done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/auth-password-change-done.html'), name="password_change_done"),
  path('accounts/password-reset/', views.UserPasswordResetView.as_view(), name='password_reset'),
  path('accounts/password-reset-confirm/<uidb64>/<token>/',views.UserPasswrodResetConfirmView.as_view(), name="password_reset_confirm"),
  path('accounts/password-reset-done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/auth-password-reset-done.html'), name='password_reset_done'),
  path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/auth-password-reset-complete.html'), name='password_reset_complete'),

  #個人介面
  path('profile/<str:username>', views.profile_page, name='profile'),
  path('profile/edit/<str:username>', views.edit_profile, name='edit_profile'),
  
  #問卷
  path('add_questionnaire/', views.add_questionnaire_view, name='add_questionnaire'),
  path('questionnaire_list/', views.questionnaire_list_view, name='questionnaire_list'),
  path('update_response/', views.update_response_view, name='update_response'),
  path('delete_questionnaire/<int:pk>/', views.delete_questionnaire_view, name='delete_questionnaire'),
  path('answer_list/<int:pk>/', views.answer_list_view, name='answer_list'),
  path('answer_history/<int:pk>/<str:username>/', views.answer_history, name='answer_history'),
  
  
  path('google-oauth/', views.redirect_to_google_oauth, name='google_oauth'),
  path('oauth2callback/', views.oauth2callback, name='oauth_callback'),
  
  
  # Components
  path('components/button/', views.bc_button, name='bc_button'),
  path('components/badges/', views.bc_badges, name='bc_badges'),
  path('components/breadcrumb-pagination/', views.bc_breadcrumb_pagination, name='bc_breadcrumb_pagination'),
  path('components/collapse/', views.bc_collapse, name='bc_collapse'),
  path('components/tabs/', views.bc_tabs, name='bc_tabs'),
  path('components/typography/', views.bc_typography, name='bc_typography'),
  path('components/feather-icon/', views.icon_feather, name='icon_feather'),
]
