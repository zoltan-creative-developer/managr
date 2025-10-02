from django.shortcuts import render

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from apps.models import (
    EmployeePreference, Employee, ShiftType, ScheduleAssignment
)

import json
from datetime import datetime

def management_shift_request_view(request):
    """Custom shift request view that renders the management-shift-request.html template"""
    context = {
        'title': 'Shift Request',
        'welcome_message': 'Welcome to the shift request page.',
    }
    return render(request, 'apps/shiftrequest/templates/management-shift-request.html', context)

def employee_shift_request_view(request):
    emp_pref = EmployeePreference.objects.filter(employee=request.user.employee).first()
    context = {
        'employee_preferences': emp_pref
    }
    
    return render(request, 'apps/shiftrequest/templates/shiftrequest/employee-shift-request.html', context)

def get_employee_shift_requests(request, employee_id):
    """Fetch shift requests for a specific employee"""
    employee = get_object_or_404(Employee, id=employee_id)
    return JsonResponse(list(shift_requests), safe=False)