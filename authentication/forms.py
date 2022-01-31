from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, PasswordChangeForm
from django.forms import fields
from .models import User

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email','first_name','last_name','password1', 'password2', 'mobile_number')


class LoginForm(forms.Form):

    email = forms.EmailField(required=True)
    password = forms.CharField(required= True, max_length=255)
    class Meta:
        fields= ('email', 'password')


class PasswordResetRequestForm(PasswordResetForm):

    class Meta:
        fields = ('email')


class PasswordResetChangeForm(forms.Form):

    password1 = forms.CharField(required= True, max_length=255)
    password2 = forms.CharField(required= True, max_length=255)

    class Meta:
        fields = ('password1','password2')

    def clean(self) :
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']

        if password1 != password2:
            raise forms.ValidationError("The two password fields didn’t match.")
            
        return self.cleaned_data


class UserProfileUpdateForm(forms.Form):

    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    mobile_number = forms.CharField(max_length=15, required=False)

    class Meta:
        fields = ('first_name', 'last_name', 'mobile_number')