from django import forms
from django.contrib.auth.forms import UserCreationForm
from account.models import Account
from django.contrib.auth import authenticate

class RegistrationForm(UserCreationForm):

    email = forms.EmailField(max_length=255,help_text='Enter a Valid Email.')

    class Meta:
        model = Account
        fields = ('email','username','password1','password2')

    def clean__email(self):
        email = self.cleaned_data['email'].lower()
        try:
            account = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return email
        raise forms.ValidationError(f'Email - {email} is already in use.')

    def clean__username(self):
        username = self.cleaned_data['username'].lower()
        try:
            account = Account.objects.get(username=username)
        except Account.DoesNotExist:
            return username
        raise forms.ValidationError(f'Username - {username} is already in use.')

class AccountAuthenticationForm(forms.ModelForm):
    email = forms.EmailField(max_length=255,label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ('email', 'password')

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email,password=password):
                raise forms.ValidationError("Invalid Credentials!")

class AccountUpdateForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ('username', 'email', 'profile_image', 'hide_email')

    def clean__email(self):
        email = self.cleaned_data['email'].lower()
        try:
            account = Account.objects.exclude(pk=self.instance.pk).get(email=email)
        except Account.DoesNotExist:
            return email
        raise forms.ValidationError(f'Email - {email} is already in use!')

    def clean__username(self):
        username = self.cleaned_data['username'].lower()
        try:
            account = Account.objects.exclude(pk=self.instance.pk).get(username=username)
        except Account.DoesNotExist:
            return username
        raise forms.ValidationError(f'username - {username} is already in use!')

    def save(self, commit=True):
        account = super(AccountUpdateForm, self).save(commit=False)
        account.username = self.cleaned_data['username']
        account.email = self.cleaned_data['email'].lower()
        account.profile_image = self.cleaned_data['profile_image']
        account.hide_email = self.cleaned_data['hide_email']
        if commit:
            account.save()
        return account

    