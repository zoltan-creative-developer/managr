from django.urls import path
from apps.staffplanner.views import management_headcount_planning_view, management_role_planning_view, show_employee_schedule
from datetime import date

urlpatterns = [
    path('management/headcount-planning/', management_headcount_planning_view, {'year': date.today().year, 'month': date.today().month}, name='management_headcount_planning'),
#    path('management/headcount-planning/', show_employee_schedule, {'year': 2025, 'month': 10}, name='management_headcount_planning'),
    path('management/role-planning/', management_role_planning_view, name='management_role_planning'),
]