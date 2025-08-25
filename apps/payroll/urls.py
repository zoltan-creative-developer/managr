from django.urls import path
from apps.payroll.views import management_payroll_view

urlpatterns = [
    path('management/payroll/', management_payroll_view, name='management_payroll'),
]