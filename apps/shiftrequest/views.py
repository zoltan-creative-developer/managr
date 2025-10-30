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
    Employee,
    EmployeeRequests,
    ScheduleDayCell,
)

from django.db import transaction, IntegrityError

@staff_member_required
def management_shift_request_view(request):
    """Custom shift request view that renders the management-shift-request.html template"""
    context = {
        'title': 'Shift Request',
        'shift_requests': EmployeeRequests.objects.filter(year=datetime.now().year, month=datetime.now().month),
    }
    return render(request, 'shiftrequest/management-shift-request.html', context)

@ensure_csrf_cookie
@staff_member_required
def show_calendar(request, year, month):
    """
    Rendereli az október hónap heteit soronként. Üres cellák 0 helyére jelennek meg.
    """
    __year = year
    __month = month
    weeks = calendar.monthcalendar(__year, __month)
    emp=Employee.objects.filter(user=request.user).first()

    day_colors = {}
    for day in range(1, calendar.monthrange(__year, __month)[1] + 1):
        day_colors[str(day)] = 'green'
    if not EmployeeRequests.objects.filter(employee=emp).exists():
        with transaction.atomic():
            try:
                obj, created = EmployeeRequests.objects.update_or_create(
                    user=request.user,
                    hire_date=date(__year, __month, 1),
                    is_active=True,
                )
                emp_req = obj
            except IntegrityError:
                pass
    else:
        emp_req=EmployeeRequests.objects.filter(employee=emp, year=__year, month=__month).first()
        
    if emp_req and "availability" in emp_req.request_data:
        for day in range(1, calendar.monthrange(__year, __month)[1] + 1):
            color = emp_req.request_data["availability"].get(str(day)) or emp_req.request_data["availability"].get(day)
            if color:
                # use string keys to match how we store availability in JSONField
                day_colors[str(day)] = color
    else:
        for day in range(1, calendar.monthrange(__year, __month)[1] + 1):
            day_colors[str(day)] = 'green'
    context = {
        "employee_name": (request.user.get_full_name()).capitalize(),
        'year': __year,
        'month': __month,
        'weeks': weeks,
        'day_colors': day_colors,  # dict: nap -> 'green'/'red'
    }
    return render(request, 'shiftrequest/employee-shift-request.html', context)

@require_POST
def toggle_day(request):
    """
    Ajax végpont: POST JSON/FORM 'year','month','day' -> visszaadja az új színt.
    Mentjük DayCell modellbe.
    """
    try:
        day = int(request.POST.get('day') or request.JSON.get('day'))
        month = int(request.POST.get('month') or request.JSON.get('month'))
        year = int(request.POST.get('year') or request.JSON.get('year'))
    except Exception:
        # egyszerű hiba kezelés
        try:
            # ha JSON body
            import json
            payload = json.loads(request.body.decode())
            day = int(payload.get('day'))
            month = int(payload.get('month'))
            year = int(payload.get('year'))
        except Exception:
            return HttpResponseBadRequest("Hiányzó vagy érvénytelen paraméterek.")

    target_date = date(year, month, day)
    obj, created = DayCell.objects.get_or_create(
        employee=request.user.employee, date=target_date
    )
    obj.color = 'red' if obj.color == 'green' else 'green'
    obj.save()
    emp_req = EmployeeRequests.objects.filter(employee=request.user.employee, year=year, month=month).first()
    emp_req.request_data['availability'][str(day)] = obj.color
    emp_req.save()

    return JsonResponse({'status': 'ok', 'day': day, 'color': obj.color})
