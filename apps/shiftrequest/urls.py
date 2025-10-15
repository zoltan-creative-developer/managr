from django.urls import path
from apps.printdesk import views
from apps.shiftrequest.views import management_shift_request_view, employee_shift_request_view, show_calendar, toggle_day, get_employee_shift_requests

urlpatterns = [
    path('management/', management_shift_request_view, name='management_shift_request'),
#    path('shiftrequest/employee/', employee_shift_request_view, name='employee_shift_request'),
    path('shiftrequest/employee/', show_calendar, {'year': 2025, 'month': 10}, name='employee_request_calendar'),  # Októberi naptár
    path('toggle-day/', toggle_day, name='toggle_day'),  # Ajax végpont
    path('employee/<int:employee_id>/requests/', get_employee_shift_requests, name='get_employee_shift_requests'),
]