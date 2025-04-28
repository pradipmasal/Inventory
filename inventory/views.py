from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Component, IssuedComponent, ReturnedComponent
from .forms import ComponentForm, IssueComponentForm, UserRegisterForm, StaffCreationForm, ReturnComponentForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone

# User Registration
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'inventory/register.html', {'form': form})

# User Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            error = "Invalid username or password."
            return render(request, 'inventory/login.html', {'error': error})

    return render(request, 'inventory/login.html')

# User Logout
def logout_view(request):
    logout(request)
    return redirect('login')

# Admin Dashboard
@login_required
def admin_dashboard(request):
    return render(request, 'inventory/admin_dashboard.html')

# Custom decorator: Only Super Admin can access
def superuser_required(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_superuser)(view_func)
    return decorated_view_func

@superuser_required
def create_staff(request):
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff_success')  # after creating staff
    else:
        form = StaffCreationForm()
    return render(request, 'inventory/create_staff.html', {'form': form})

def staff_success(request):
    return render(request, 'inventory/staff_success.html')

@superuser_required
def staff_list(request):
    staff_users = User.objects.filter(is_staff=True, is_superuser=False)  # only staff, not superusers
    return render(request, 'inventory/staff_list.html', {'staff_users': staff_users})

@superuser_required
def deactivate_staff(request, staff_id):
    staff_user = get_object_or_404(User, id=staff_id, is_staff=True, is_superuser=False)

    if request.method == 'POST':
        staff_user.is_active = False
        staff_user.save()
        return redirect('staff_list')  # After deactivation, redirect back to staff list

@superuser_required
def activate_staff(request, staff_id):
    staff_user = get_object_or_404(User, id=staff_id, is_staff=True, is_superuser=False)

    if request.method == 'POST':
        staff_user.is_active = True
        staff_user.save()
        return redirect('staff_list')

@superuser_required
def delete_component(request, component_id):
    component = get_object_or_404(Component, id=component_id)

    if request.method == 'POST':
        component.delete()
        return redirect('available_components')  # Redirect to the list of available components

    return render(request, 'inventory/delete_component.html', {'component': component})
        
# User Dashboard
@login_required
def user_dashboard(request):
    issued = IssuedComponent.objects.filter(user=request.user)
    return render(request, 'inventory/user_dashboard.html', {'issued': issued})

@login_required
def add_component(request):
    if request.method == 'POST':
        form = ComponentForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            category = form.cleaned_data['category']
            quantity = form.cleaned_data['quantity']
            price = form.cleaned_data['price']

            # Check if a component with same name and category exists
            component, created = Component.objects.get_or_create(
                name=name,
                category=category,
                defaults={'quantity': quantity, 'price': price}
            )

            if not created:
                # Already exists ➔ Update quantity
                component.quantity += quantity

                # Optional: update price if admin changed it
                component.price = price

                component.save()

            return redirect('admin_dashboard')
    else:
        form = ComponentForm()

    return render(request, 'inventory/add_component.html', {'form': form})


@superuser_required
def view_all_users(request):
    user_type = request.GET.get('user_type', 'all')

    if user_type == 'staff':
        users = User.objects.filter(is_staff=True, is_superuser=False)
    elif user_type == 'user':
        users = User.objects.filter(is_staff=False, is_superuser=False)
    else:
        users = User.objects.filter(is_superuser=False)

    context = {
        'users': users,
        'selected_type': user_type,
    }
    return render(request, 'inventory/user_list.html', context)

@superuser_required
def make_staff(request, user_id):
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    if request.method == 'POST':
        user.is_staff = True
        user.save()
    return redirect('view_all_users')

@superuser_required
def make_user(request, user_id):
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    if request.method == 'POST':
        user.is_staff = False
        user.save()
    return redirect('view_all_users')

# Issue Component
@login_required
def issue_component(request):
    if request.method == 'POST':
        form = IssueComponentForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            component = form.cleaned_data['component']
            quantity_issued = form.cleaned_data['quantity_issued']

            # Check if already issued
            issued_record, created = IssuedComponent.objects.get_or_create(
                user=user,
                component=component,
                defaults={'quantity_issued': quantity_issued, 'issue_date': timezone.now()}
            )

            if not created:
                # Already issued ➔ Update quantity
                issued_record.quantity_issued += quantity_issued
                issued_record.save()

            # Reduce available stock from Component
            component.quantity -= quantity_issued
            component.save()

            return redirect('admin_dashboard')
    else:
        form = IssueComponentForm()

    return render(request, 'inventory/issue_component.html', {'form': form})

@login_required
def available_components(request):
    components = Component.objects.all()
    return render(request, 'inventory/available_components.html', {'components': components})

@login_required
def issued_components(request):
    issued = IssuedComponent.objects.filter(user=request.user, returned=False)
    return render(request, 'inventory/issued_components.html', {'issued': issued})

def return_component(request):
    if request.method == 'POST':
        form = ReturnComponentForm(request.POST)
        if form.is_valid():
            returned_component = form.save(commit=False)

            # Find the issued record
            issued_record = IssuedComponent.objects.filter(
                user=returned_component.user,
                component=returned_component.component
            ).first()

            if issued_record:
                returned_component.quantity_issued = issued_record.quantity_issued
                returned_component.issue_date = issued_record.issue_date

                # 1. Update Component stock
                component = returned_component.component
                component.quantity += returned_component.quantity_returned
                component.save()

                # 2. Update or delete IssuedComponent
                if returned_component.quantity_returned >= issued_record.quantity_issued:
                    # If fully returned or over-returned, delete the issued record
                    issued_record.delete()
                else:
                    # If partial return, reduce the quantity_issued
                    issued_record.quantity_issued -= returned_component.quantity_returned
                    issued_record.save()

                # 3. Save the ReturnedComponent record
                returned_component.save()

                return redirect('admin_dashboard')
    else:
        form = ReturnComponentForm()

    return render(request, 'inventory/return_component.html', {'form': form})

def load_user_components(request):
    user_id = request.GET.get('user')
    issued_components = IssuedComponent.objects.filter(user_id=user_id).select_related('component')
    components = [{'id': c.component.id, 'name': c.component.name} for c in issued_components]
    return JsonResponse({'components': components})

@login_required
def returned_components(request):
    returned = ReturnedComponent.objects.filter(user=request.user)
    return render(request, 'inventory/returned_components.html', {'returned': returned})

@superuser_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id, is_superuser=False)

    if request.method == 'POST':
        # Step 1: Check issued components
        issued_components = IssuedComponent.objects.filter(user=user)

        # Step 2: Return all issued components
        for issued in issued_components:
            component = issued.component
            component.quantity += issued.quantity_issued  # Return back the stock
            component.save()
            issued.delete()  # Remove issued record after returning

        # Step 3: Delete user
        user.delete()

        return redirect('view_all_users')

    return render(request, 'inventory/delete_user_confirm.html', {'user_obj': user})

@superuser_required
def user_dashboard_admin_view(request, user_id):
    if not request.user.is_staff:
        return redirect('home')  # Optional: only allow staff/admins

    user = get_object_or_404(User, id=user_id)

    issued = IssuedComponent.objects.filter(user=user)
    returned = ReturnedComponent.objects.filter(user=user)

    context = {
        'viewed_user': user,
        'issued': issued,
        'returned': returned,
    }
    return render(request, 'inventory/user_dashboard_admin_view.html', context)