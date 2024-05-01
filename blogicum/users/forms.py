from django.contrib.auth.forms import UserCreationForm
from django import forms

from django.contrib.auth import get_user_model


class SignUpForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = '__all__'

