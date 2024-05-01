from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView

from django.urls import include, path, reverse_lazy
from django.contrib.auth.urls import urlpatterns as auth_urls

import views
app_name = 'users'
urlpatterns = [
    path('<str:username>', views.ProfileCreateView.as_view(), name='profile'),

]


