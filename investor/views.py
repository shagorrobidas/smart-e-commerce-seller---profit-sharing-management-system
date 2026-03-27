"""Frontend Template Views for Investor App."""

from django.views.generic import TemplateView

class InvestorDashboardView(TemplateView):
    template_name = 'investor/dashboard.html'

class InvestorAgreementsView(TemplateView):
    template_name = 'investor/agreements.html'

class InvestorInvestView(TemplateView):
    template_name = 'investor/invest.html'

class InvestorReportsView(TemplateView):
    template_name = 'investor/reports.html'
