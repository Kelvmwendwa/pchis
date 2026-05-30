from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:role_redirect')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)

            return redirect('dashboard:role_redirect')
        else:

            messages.error(request, "Authentication failed. Please check your credentials.")

    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Your session has ended. Please log in to continue.")
    return redirect('accounts:login')