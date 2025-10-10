from django.urls import path
from apps.shiftrequest.views import management_shift_request_view, employee_shift_request_view, get_employee_shift_requests

urlpatterns = [
    path('management/', management_shift_request_view, name='management_shift_request'),
    path('shiftrequest/employee/', employee_shift_request_view, name='employee_shift_request'),
    path('employee/<int:employee_id>/requests/', get_employee_shift_requests, name='get_employee_shift_requests'),
]