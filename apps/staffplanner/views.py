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
    WorkArea,
    WorkRole,
    Employee,
    ShiftType,
    StaffSchedules,
    EmployeeRequests,
)
from django.db import transaction, IntegrityError

@staff_member_required
def management_headcount_planning_view(request, year, month):
    __year = year
    __month = month
    weeks = calendar.monthcalendar(__year, __month)
    day_list = [str(d) for d in range(1, calendar.monthrange(__year, __month)[1] + 1)]
    employee_qs = Employee.objects.filter(user__is_active=True)
    employee_requests = EmployeeRequests.objects.filter(year=__year, month=__month)
    day_shift_colors = {}

    for employee in employee_qs:
        colors = {}
        for day in day_list:
            if not employee_requests.filter(employee=employee, year=__year, month=__month).exists():
                colors[day] = ['red', 'red']
            else:
                req = employee_requests.get(employee=employee, year=__year, month=__month).request_data
                v = req.get(day)
                colors[day] = [v, v]

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
        'title': 'Létszám tervezés',
        'welcome_message': 'Üdvözlünk a létszám tervezés oldalon!',
        'year': __year,
        'month': __month,
        'day_list': day_list,
        'daytime_list': [['de', 'du'] for _ in day_list],
        'days_in_month': calendar.monthrange(__year, __month)[1],
        'month_name': calendar.month_name[__month],
        'weeks': weeks,
        'employee_names': {emp.id: " ".join([emp.user.last_name, emp.user.first_name]) for emp in employee_qs},
        'day_shift_colors': day_shift_colors,
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