from django.urls import path
from apps.shiftrequest.views import management_shift_request_view, employee_shift_request_view

urlpatterns = [
    path('management/', management_shift_request_view, name='management_shift_request'),
    path('employee/', employee_shift_request_view, name='employee_shift_request'),    
]