from django.urls import path
from apps.printdesk import views
from apps.shiftrequest.views import employee_shift_request_view, management_shift_request_view, toggle_day, set_shiftrequest_dates, set_employee_shiftrequest_dates
from django.contrib.auth.decorators import login_required
from datetime import date

urlpatterns = [
    path('set-dates/', set_shiftrequest_dates, name='set_shiftrequest_dates'),
    path('set-employee-dates/', set_employee_shiftrequest_dates, name='set_employee_shiftrequest_dates'),
    path('management/<int:year>/<int:month>/', management_shift_request_view, name='management_shift_request'),
    path('management/', management_shift_request_view, {'year': date.today().year, 'month': date.today().month}, name='management_shift_request'),
    path('employee/<int:year>/<int:month>/', employee_shift_request_view, name='employee_shift_request'),
    path('employee/', employee_shift_request_view, {'year': date.today().year, 'month': date.today().month}, name='employee_shift_request'),
    path('toggle-day/', toggle_day, name='toggle_day'),  # Ajax végpont
]