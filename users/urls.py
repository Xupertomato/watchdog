from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

app_name='users'

urlpatterns = [    
    path('login/', LoginView.as_view(template_name='users/login.html'), name="login"),
    path('logout/', views.logout_view, name='logout'),
    path('register_base/', views.register_base, name='register_base'),
    path('register_elder/', views.register_elder, name='register_elder'),
    path('register_related/', views.register_related, name='register_related'),
    path('register_manager/', views.register_manager, name='register_manager'),
   
]
