from django.urls import path
from apps.printdesk import views
from apps.shiftrequest.views import management_shift_request_view,show_calendar, toggle_day

urlpatterns = [
    path('management/', management_shift_request_view, name='management_shift_request'),
    path('shiftrequest/employee/', show_calendar, {'year': 2025, 'month': 10}, name='employee_request_calendar'),  # Októberi naptár
    path('toggle-day/', toggle_day, name='toggle_day'),  # Ajax végpont
]