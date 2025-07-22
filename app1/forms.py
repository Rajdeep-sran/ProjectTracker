from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Project, Milestone

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'id_password1'  # For toggle eye icon
        })
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'id': 'id_password2'  # For toggle eye icon
        })
    )

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.username = self.cleaned_data['email']  # Set email as username
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'start_date', 'end_date']

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in ['start_date', 'end_date']:
                field.widget.attrs.update({
                    'class': 'form-control flatpickr',
                    'type': 'text',  # <-- key change here!
                    'placeholder': 'YYYY-MM-DD'
                })
            else:
                field.widget.attrs.update({'class': 'form-control'})

class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['title', 'due_date', 'priority', 'is_completed']

    def __init__(self, *args, **kwargs):
        super(MilestoneForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "priority":
                field.widget.attrs.update({'class': 'form-select'})
            elif name == "due_date":
                field.widget.attrs.update({
                    'class': 'form-control flatpickr',
                    'type': 'text',
                    'placeholder': 'YYYY-MM-DD'
                })
            elif name == "is_completed":
                # 👇 This is the missing fix!
                field.widget.attrs.update({
                    'class': 'form-check-input',
                    'style': 'margin-top: 5px; transform: scale(1.3);'
                })
            else:
                field.widget.attrs.update({'class': 'form-control'})
