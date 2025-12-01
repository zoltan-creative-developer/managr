from django.urls import path
from apps.staffplanner.views import set_staffplanner_dates, management_headcount_planning_view, management_role_planning_view, toggle_shift
from datetime import date

urlpatterns = [
    path('set-dates/', set_staffplanner_dates, name='set_staffplanner_dates'),
    path('management/headcount-planning/<int:year>/<int:month>/', management_headcount_planning_view, name='management_headcount_planning'),
    path('management/headcount-planning/', management_headcount_planning_view, {'year': date.today().year, 'month': date.today().month}, name='management_headcount_planning'),
    path('toggle-shift/', toggle_shift, name='toggle_shift'),  # Ajax végpont
    path('management/role-planning/', management_role_planning_view, name='management_role_planning'),
]