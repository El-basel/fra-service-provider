from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
from .forms import *
# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard/')
    else:
        return render(request, 'services/index.html')
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            if user is not None:
                login(request, user)
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid username or password")
                return render(request, "services/login.html", {'form': form})
    else:
        form = LoginForm()
    return render(request, 'services/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/')

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
        else:
            # messages.error(request, "Invalid username or password")
            return render(request, "services/signup.html", {'form': form})
    else:
        form = SignupForm()
        return render(request, 'services/signup.html', {'form': form})


@login_required
def dashboard(request):
    user = request.user.userprofile
    services = Service.objects.all()
    content = {'user': user, 'services': services}
    if user.role == 'admin':
        template_name = 'services/admin_dashboard.html'
    elif user.role == 'reviewer':
        template_name = 'services/reviewer_dashboard.html'
    else:
        template_name = 'services/applicant_dashboard.html'
    return render(request, template_name, content)

@login_required
def request_service(request):
    user = request.user.userprofile
    if user.role != 'applicant':
        return redirect('dashboard')
    if request.method == 'POST':
        form = RequestServiceForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            return redirect("dashboard")
        else:
            return render(request, "services/request_service.html", {'form': form})
    else:
        form = RequestServiceForm()
        return render(request, "services/request_service.html", {'form': form})

@login_required
def service_approval(request, pk=0):
    user = request.user.userprofile
    if user.role != 'admin':
        return redirect('dashboard')
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceApprovalForm(request.POST)
        if form.is_valid():
            form.save(service.pk)
            return redirect("dashboard")
    else:
        form = ServiceApprovalForm()
    return render(request, 'services/admin_service_approval.html', {'form': form, 'service': service})

@login_required
def delete_service(request, pk):
    user = request.user.userprofile
    service = get_object_or_404(Service, pk=pk)
    if service.applicant.pk != request.user.userprofile.pk:
        return redirect('dashboard') # display and error message that this user isn't allowed to delete this service
    if request.method == 'GET':
        if service.status == service.Status.PENDING:
            service.delete()
    return redirect("dashboard")

@login_required
def service_review(request, pk):
    user = request.user.userprofile
    if user.role != 'reviewer':
        return redirect('dashboard')
    service = get_object_or_404(Service, pk=pk)
    return render(request, 'services/reviewer_service_review.html', {'service': service})

@login_required
def service_approve(request, pk):
    user = request.user.userprofile
    if user.role != 'reviewer':
        return redirect('dashboard')
    service = get_object_or_404(Service, pk=pk)
    service.status = service.Status.APPROVED
    service.save()
    return redirect("dashboard")

@login_required
def service_reject(request, pk):
    user = request.user.userprofile
    if user.role != 'reviewer':
        return redirect('dashboard')
    service = get_object_or_404(Service, pk=pk)
    service.status = service.Status.REJECTED
    service.save()
    return redirect("dashboard")

@login_required
def pay_service(request, pk):
    user = request.user.userprofile
    if user.role != 'applicant':
        return redirect('dashboard')
    service = get_object_or_404(Service, pk=pk)
    if service.applicant.pk != request.user.userprofile.pk:
        return redirect('dashboard')
    service.paid = True
    service.save()
    return redirect("dashboard")

@login_required
def history(request):
    user = request.user.userprofile
    if user.role == 'applicant':
        return redirect('dashboard')
    services = Service.objects.all()
    content = {'user': user, 'services': services}
    return render(request, 'services/history.html', content)