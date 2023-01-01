from django.shortcuts import render, redirect
from account.forms import RegistrationForm , AccountAuthenticationForm
from django.http import HttpResponse
from django.contrib.auth import authenticate , login , logout

# Create your views here.

def register_view(request, *args , **kwargs):

    user = request.user
    context = {}
    if user.is_authenticated:
        return HttpResponse(f'You are already authenticated as {user.username} with email - {user.email}')
    
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()

            email = form.cleaned_data['email'].lower()
            raw_password =  form.cleaned_data['password1']
            account = authenticate(email=email,password=raw_password)
            login(request, account)
            destination = kwargs.get('next')
            if destination:
                return redirect(destination)
            else:
                return redirect('home')
        else:
            context['registration_form'] = form
        
    else:
        form = RegistrationForm()
        context['registration_form'] = form
    
    return render(request, 'account/register.html',context)

def logout_view(request):
    logout(request)
    return redirect('home')

def login_view(request, *args, **kwargs):

    context = {}
    user = request.user
    if user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email')
            password = request.POST.get('password')
            user =  authenticate(email=email, password=password)
            if user:
                login(request, user)
                destination = kwargs.get('next')
                if destination:
                    return redirect(destination)
                else:
                    return redirect('home')
        else:
            context['login_form'] = form

    return render(request, 'account/login.html', context)