import calendar
from urllib import request
from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseBadRequest
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from datetime import datetime, date, timedelta
from apps.models import (
    CustomUserManager,
    CustomUser,
    WorkArea,
    WorkRole,
    Employee,
    ShiftType,
    StaffSchedules,
    ScheduleDayCell,
    EmployeeRequests,
)
from django.db import transaction, IntegrityError

@staff_member_required
def management_headcount_planning_view(request):
    context = {
        'title': 'Headcount Planning',
        'welcome_message': 'Welcome to the headcount planning page.',
    }
    return render(request, 'staffplanner/management-headcount-planning.html', context)

@staff_member_required
def management_role_planning_view(request):
    """Custom role planning view that renders the management-role-planning.html template"""
    context = {
        'title': 'Role Planning',
        'welcome_message': 'Welcome to the role planning page.',
    }
    return render(request, 'staffplanner/management-role-planning.html', context)

@staff_member_required
def show_employee_schedule(request, year, month):
    __year = year
    __month = month
    days = range(1, calendar.monthrange(__year, __month)[1] + 1)
    weeks = calendar.monthcalendar(__year, __month)  # minden hét: lista 7 elemmel, 0 ha nincs nap

    day_shift_colors = {}
    employee_qs = Employee.objects.filter(user__is_active=True)
    print("Active employees:", employee_qs)

    # pass the queryset so templates can access employee.id and name together

    employee_requests = EmployeeRequests.objects.filter(year=__year, month=__month)
    for employee in employee_qs:
        colors = {}
        if not employee_requests.filter(employee=employee, year=__year, month=__month).exists():
            days_in_month = calendar.monthrange(__year, __month)[1]
            for day in range(1, days_in_month + 1):
                colors[str(day)] = 'red'
        else:
            colors=EmployeeRequests.objects.filter(employee=employee, year=__year, month=__month).first().request_data
        
        if not StaffSchedules.objects.filter(employee=employee, year=__year, month=__month).exists():
            try:
                with transaction.atomic():
                    obj, created = StaffSchedules.objects.update_or_create(
                        employee=employee, year=__year, month=__month,
                        defaults={'schedule_data': colors}
                    )
            except IntegrityError:
                obj = StaffSchedules.objects.get(employee=employee, year=__year, month=__month)
            colors = obj.schedule_data

        day_shift_colors[employee.id] = colors

    context = {
        'title': 'Employee Schedule',
        'days': days,
        'weeks': weeks,
        'employee_qs': employee_qs,
        'day_shift_colors': day_shift_colors,
    }
    return render(request, 'staffplanner/management-staff-planner.html', context)
