from django import forms
from .models import Component, IssuedComponent
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# class ComponentForm(forms.ModelForm):
#     class Meta:
#         model = Component
#         fields = '__all__'

class ComponentForm(forms.ModelForm):
    class Meta:
        model = Component
        fields = ['name', 'category', 'quantity', 'price']

class IssueComponentForm(forms.ModelForm):
    class Meta:
        model = IssuedComponent
        fields = ['user', 'component', 'quantity_issued', 'expected_return_date']

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class StaffCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # hash password
        user.is_staff = True  # make staff
        if commit:
            user.save()
        return user
