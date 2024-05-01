from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.
class ProfileCreateView(CreateView,LoginRequiredMixin):
    model = User
