from django.urls import path
from apps.printdesk import views
from apps.shiftrequest.views import employee_shift_request_view, management_shift_request_view, toggle_day

urlpatterns = [
    path('management/', management_shift_request_view, {'year': 2025, 'month': 11}, name='management_shift_request'),
    path('shiftrequest/employee/', employee_shift_request_view, {'year': 2025, 'month': 11}, name='employee_request_calendar'),  # Novemberi naptár
    path('toggle-day/', toggle_day, name='toggle_day'),  # Ajax végpont
]