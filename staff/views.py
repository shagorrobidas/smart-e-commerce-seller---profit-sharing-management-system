"""Frontend Template Views for Staff App."""

from django.views.generic import TemplateView

class StaffDashboardView(TemplateView):
    template_name = 'staff/dashboard.html'

class StaffInventoryView(TemplateView):
    template_name = 'staff/inventory.html'

class StaffOrdersView(TemplateView):
    template_name = 'staff/orders.html'

class StaffTasksView(TemplateView):
    template_name = 'staff/tasks.html'

class StaffMessagesView(TemplateView):
    template_name = 'staff/messages.html'

class StaffReportsView(TemplateView):
    template_name = 'staff/reports.html'
