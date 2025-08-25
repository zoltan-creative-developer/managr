from django.urls import path
from apps.staffplanner.views import management_headcount_planning_view, management_role_planning_view

urlpatterns = [
    path('management/headcount-planning/', management_headcount_planning_view, name='management_headcount_planning'),
    path('management/role-planning/', management_role_planning_view, name='management_role_planning'),
]