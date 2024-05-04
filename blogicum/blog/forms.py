from django import forms
from django.contrib.auth import get_user_model

from blog.models import Post, Comment

User = get_user_model()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ("author",)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
