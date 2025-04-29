from django import forms
from .models import Component, IssuedComponent, ReturnedComponent
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
        fields = ['component', 'user', 'quantity_issued']
        widgets = {
            'component': forms.Select(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'quantity_issued': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ReturnComponentForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'user-select'})
    )
    component = forms.ModelChoiceField(
        queryset=Component.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'component-select'})
    )

    class Meta:
        model = ReturnedComponent
        fields = ['user', 'component', 'quantity_returned']

    def __init__(self, *args, **kwargs):
        super(ReturnComponentForm, self).__init__(*args, **kwargs)
        if 'user' in self.data:
            try:
                user_id = int(self.data.get('user'))
                issued_components = IssuedComponent.objects.filter(user_id=user_id).values_list('component_id', flat=True)
                self.fields['component'].queryset = Component.objects.filter(id__in=issued_components)
            except (ValueError, TypeError):
                pass

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
