from django.urls import path
from apps.printdesk import views
from apps.shiftrequest.views import employee_shift_request_view, management_shift_request_view, toggle_day
from datetime import date

urlpatterns = [
    path('management/', management_shift_request_view, {'year': date.today().year, 'month': date.today().month}, name='management_shift_request'),
    path('shiftrequest/employee/', employee_shift_request_view, {'year': date.today().year, 'month': date.today().month}, name='employee_request_calendar'),
    path('toggle-day/', toggle_day, name='toggle_day'),  # Ajax végpont
]