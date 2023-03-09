from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import logout # 匯入logout函式
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm

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
    return render(request, 'users/register_related.html', context)

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
    return render(request, 'users/register_related.html', context)