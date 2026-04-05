"""Root-level Template Views (Login, Register, etc.)"""

from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'


class LoginView(TemplateView):
    template_name = 'login.html'


class RegisterView(TemplateView):
    template_name = 'register.html'


class ForgotPasswordView(TemplateView):
    template_name = 'forgot-password.html'


class ProfileView(TemplateView):
    template_name = 'profile.html'


class LogoutView(TemplateView):
    template_name = 'logout.html'
