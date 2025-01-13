from django import forms
from django.contrib.auth.hashers import make_password

from my_site.models import Client 


class UserUpdateForm(forms.ModelForm):
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Client.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Этот email уже используется.")
        return email
    
    class Meta:
        model = Client
        fields = ['username', 'email']
        

class PasswordChangeForm(forms.Form):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Новый пароль'}),
        label="Новый пароль"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторите пароль'}),
        label="Повторите новый пароль"
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')

        if password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")

        return cleaned_data

    def save(self, user):
        user.password = make_password(self.cleaned_data['new_password1'])
        user.save()
