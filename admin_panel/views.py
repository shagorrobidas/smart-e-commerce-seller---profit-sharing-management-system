"""Frontend Template Views for Admin Panel."""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class AdminDashboardView(TemplateView):
    template_name = 'admin_panel/dashboard.html'

class AdminUsersView(TemplateView):
    template_name = 'admin_panel/users.html'

class AdminTasksView(TemplateView):
    template_name = 'admin_panel/tasks.html'

class AdminReportsView(TemplateView):
    template_name = 'admin_panel/reports.html'

class AdminSettingsView(TemplateView):
    template_name = 'admin_panel/settings.html'

class AdminMessagesView(TemplateView):
    template_name = 'admin_panel/messages.html'
