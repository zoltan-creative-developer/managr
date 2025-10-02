import calendar
from django.shortcuts import render

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from apps.models import (
    CustomUserManager,
    CustomUser,
    WorkArea,
    WorkRole,
    Employee,
    ShiftType,
    MonthlySchedule,
    ScheduleAssignment,
    EmployeePreference,
    ScheduleStatistics,
)

import json
from datetime import datetime

@staff_member_required
def management_shift_request_view(request):
    """Custom shift request view that renders the management-shift-request.html template"""
    context = {
        'title': 'Shift Request',
        'welcome_message': 'Welcome to the shift request page.',
    }
    return render(request, 'apps/shiftrequest/templates/management-shift-request.html', context)

def employee_shift_request_view(request):
    year = datetime.now().year
    month = datetime.now().month
    days = [day for day in range(1, calendar.monthrange(2025, 10)[1] + 1)]
    # emp = Employee.objects.filter(user=request.user).first()
    # emp_pref = EmployeePreference.objects.filter(employee=emp).first()

    # current_schedule = MonthlySchedule.objects.filter(
    #     _year=year,
    #     _month=month
    # ).first()
    
    # if not current_schedule:
    #     # Ha nincs aktuális beosztás, keressük a legutolsót
    #     current_schedule = MonthlySchedule.objects.order_by('-year', '-month').first()
    
    # if not current_schedule:
    #     # Ha egyáltalán nincs beosztás, üres adatokkal dolgozunk
    #     user = request.user
    #     role = getattr(user, 'role', None)
    #     work_area = getattr(user, 'work_area', None)
    #     nevek = len(current_schedule.employees)
    #     days_in_month = len(current_schedule.days_in_month)
    #     context = {
    #         'error_message': 'Nincs elérhető beosztás. Kérjük, hozzon létre egyet a management parancsokkal.',
    #         'available_schedules': [],
    #         'matrix_data': None,
    #         'days': days,
    #     }
    #     return render(request, 'apps/shiftrequest/templates/shiftrequest/employee-shift-request.html', context)

    # context = {
    #     'employee_preferences': emp_pref
    # }

    context = {
        'error_message': 'Nincs elérhető beosztás. Kérjük, hozzon létre egyet a management parancsokkal.',
        'available_schedules': [],
        'matrix_data': None,
        'days': days,
    }

    return render(request, 'apps/shiftrequest/templates/shiftrequest/employee-shift-request.html', context)

def get_employee_shift_requests(request, employee_id):
    """Fetch shift requests for a specific employee"""
    employee = get_object_or_404(Employee, id=employee_id)
    return JsonResponse(list(shift_requests), safe=False)