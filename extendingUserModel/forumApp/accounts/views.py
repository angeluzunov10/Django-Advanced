from django.urls import reverse_lazy
from django.views.generic import CreateView
from forumApp.accounts.forms import CustomUserCreateForm


class UserRegisterView(CreateView):
    form_class = CustomUserCreateForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('index')
