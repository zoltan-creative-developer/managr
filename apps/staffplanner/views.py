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
from django.db import DatabaseError, OperationalError, transaction, IntegrityError
import json
from django.core.exceptions import PermissionDenied

@staff_member_required
def management_headcount_planning_view(request, year, month):
    __year = year
    __month = month
    weeks = calendar.monthcalendar(__year, __month)
    day_list = [str(d) for d in range(1, calendar.monthrange(__year, __month)[1] + 1)]
    hu_day_map = {'Monday':'Hétfő','Tuesday':'Kedd','Wednesday':'Szerda','Thursday':'Csütörtök','Friday':'Péntek','Saturday':'Szombat','Sunday':'Vasárnap'}
    hu_day_map3 = {'Monday':'H','Tuesday':'K','Wednesday':'Sze','Thursday':'Cs','Friday':'P','Saturday':'Szo','Sunday':'V'}
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
        else:
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
        'days_of_the_week': ['H', 'K', 'Sz', 'Cs', 'P', 'Sz', 'V'],
        'days_of_week_in_month': [
            hu_day_map3.get(calendar.day_name[calendar.weekday(__year, __month, day)], '') 
            for day in range(1, calendar.monthrange(__year, __month)[1] + 1)
        ],
        'weekend_days': [day for day in day_list if calendar.weekday(__year, __month, int(day)) >= 5],
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


@require_POST
def toggle_shift(request):
    try:
        payload = json.loads(request.body.decode())
        emp = payload.get('emp')
        shift_str = payload.get('shift')
        if shift_str not in ("de", "du"):
            return JsonResponse({'error': 'Érvénytelen shift érték'}, status=400)
        shift = 0 if shift_str == "de" else 1
        day = int(payload.get('day'))
        month = int(payload.get('month'))
        year = int(payload.get('year'))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Érvénytelen JSON lekérdezés, a dátum mezők hiányoznak vagy érvénytelenek'}, status=400)
    except PermissionDenied:
        return JsonResponse({'error': 'Nincs jogosultságod a dátum lekéréséhez'}, status=403)

    # Lookup by employee id (emp may be an id or Employee instance elsewhere);
    # using employee_id avoids accidental queryset mismatches.
    schedule = StaffSchedules.objects.filter(employee=emp, year=year, month=month).first()
    if not schedule:
        return JsonResponse({'error': 'Nincs még létrehozva műszak ehhez a dolgozóhoz és hónaphoz'}, status=404)

    with transaction.atomic():
        try:
            schedule = StaffSchedules.objects.select_for_update().get(pk=schedule.pk)
        except DatabaseError:
            return JsonResponse({'error': 'Adatbázis hiba történt a műszak igény zárolásakor'}, status=500)

        # Defensive normalization for legacy/bad data
        sd = schedule.schedule_data
        # If sd is a list (legacy [colors, colors]), take the first element if it's a dict
        if isinstance(sd, list) and len(sd) > 0 and isinstance(sd[0], dict):
            sd = sd[0]
        if not isinstance(sd, dict):
            sd = {}

        day_key = str(day)
        dayval = sd.get(day_key)
        # If missing or malformed, normalize to two-element list
        if not isinstance(dayval, list):
            if isinstance(dayval, str):
                dayval = [dayval, dayval]
            else:
                dayval = ['red', 'red']

        # Ensure at least two elements
        if len(dayval) < 2:
            dayval = (dayval + ['red', 'red'])[:2]

        # Toggle
        try:
            dayval[shift] = 'green' if dayval[shift] == 'red' else 'red'
        except Exception:
            return JsonResponse({'error': 'Hiba a nap értékének módosításakor'}, status=500)

        sd[day_key] = dayval
        schedule.schedule_data = sd
        try:
            schedule.save()
            print(f"Updated schedule_data for employee {emp} on {year}-{month}-{day}: {StaffSchedules.objects.get(pk=schedule.pk).schedule_data[day_key]}")
        except DatabaseError:
            return JsonResponse({'error': 'Adatbázis hiba mentéskor'}, status=500)

    return JsonResponse({'status': 'ok', 'day': day, 'color': schedule.schedule_data[str(day)][shift]})
