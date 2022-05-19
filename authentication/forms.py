from distutils.command.clean import clean
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, PasswordChangeForm
from django.forms import fields
from .models import User
from members.models import Member

class RegistrationForm(UserCreationForm):
    email = forms.CharField(max_length=30, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    middle_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=True)
    mobile_number = forms.CharField(max_length=30, required=False)
    gender = forms.CharField(max_length=30, required=True)
    class Meta:
        model = User
        fields=('email',)


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

class PasswordChangeRequiredForm(forms.Form):

    password = forms.CharField(required= True, max_length=255)
    password1 = forms.CharField(required= True, max_length=255)
    password2 = forms.CharField(required= True, max_length=255)

    class Meta:
        fields = ('password','password1','password2')

    def clean_password(self):
        password = self.cleaned_data['password']

    def clean(self) :
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']

        if password1 != password2:
            raise forms.ValidationError("The two password fields didn’t match.")
            
        return self.cleaned_data


class UserProfileUpdateForm(forms.Form):

    first_name = forms.CharField(max_length=30, required=True)
    middle_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=True)
    mobile_number = forms.CharField(max_length=20, required=True)

    class Meta:
        fields = ('first_name', 'last_name',)

class PasswordChangeRequiredForm():
    new_password1 = forms.CharField(required= True, max_length=255)
    new_password2 = forms.CharField(required= True, max_length=255)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PasswordChangeRequiredForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self) :
        new_password1 = self.cleaned_data['new_password1']
        new_password2 = self.cleaned_data['new_password2']

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError("The two password fields didn’t match.")
            
        return self.cleaned_data

    def save(self, commit=True):
        """
        Saves the new password.
        """
        self.user.set_password(self.cleaned_data["new_password1"])
        self.user.password_change = True
        if commit:
            self.user.save()
        return self.user