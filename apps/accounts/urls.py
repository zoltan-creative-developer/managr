from django.urls import path
from apps.accounts.views import management_login_view, management_dashboard_view, employee_login_view, employee_dashboard_view

urlpatterns = [
    path('management-login/', management_login_view, name='management_login'),
    path('management/dashboard/', management_dashboard_view, name='management_dashboard'),
    path('login/', employee_login_view, name='employee_login'),
    path('employee/', employee_dashboard_view, name='employee_dashboard'),
]