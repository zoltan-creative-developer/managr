import calendar
import traceback
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from datetime import datetime, date
from apps.models import (
    Employee,
    EmployeeRequests,
)
from django.db import DatabaseError, OperationalError, transaction, IntegrityError
import json
from django.core.exceptions import PermissionDenied

@staff_member_required
def management_shift_request_view(request, year, month):
    __year = year
    __month = month
    weeks = calendar.monthcalendar(__year, __month)

    context = {
        'title': 'Műszak igények kezelése',
        'year': __year,
        'month': __month,
        'day_list': range(1, calendar.monthrange(__year, __month)[1] + 1),
        'days_in_month': calendar.monthrange(__year, __month)[1],
        'month_name': calendar.month_name[__month],
        'weeks': weeks,        
        'shift_requests': EmployeeRequests.objects.filter(year=__year, month=__month),
    }
    return render(request, 'shiftrequest/management-shift-request.html', context)

@ensure_csrf_cookie
@login_required
def employee_shift_request_view(request, year, month):
    __year = year
    __month = month
    weeks = calendar.monthcalendar(__year, __month)

    if not Employee.objects.filter(user=request.user).exists():
        messages.error(request, "Nincs dolgozói profilod. Jelezd a rendszergazdának.")
        return redirect('employee_login')
    
    emp=Employee.objects.filter(user=request.user).first()
    
    with transaction.atomic():
        try:
            if not EmployeeRequests.objects.filter(employee=emp, year=__year, month=__month).exists():
                day_colors = {}
                for day in range(1, calendar.monthrange(__year, __month)[1] + 1):
                    day_colors[str(day)] = 'green'
                obj, created = EmployeeRequests.objects.update_or_create(
                    employee=emp,
                    year=__year,
                    month=__month,
                    defaults={'request_data': day_colors},
                )
            else:
                emp_req = EmployeeRequests.objects.select_for_update().get(
                    employee=emp,
                    year=__year,
                    month=__month,
                )
                day_colors = emp_req.request_data
        except (OperationalError, IntegrityError):
                emp_req = None
                messages.error(request, "Hiba történt a műszak igény lekérésekor.")
                print("OperationalError or IntegrityError occurred during fetching of employee request.")
                print(traceback.format_exc())
                return redirect('employee_dashboard')

    context = {
        "employee_name": (request.user.get_full_name()).capitalize(),
        'year': __year,
        'month': __month,
        'month_name': calendar.month_name[__month],
        'weeks': weeks,
        'day_colors': day_colors,  # dict: nap -> 'green'/'red'
    }
    return render(request, 'shiftrequest/employee-shift-request.html', context)

@require_POST
def toggle_day(request):
    try:
        payload = json.loads(request.body.decode())
        day = int(payload.get('day'))
        month = int(payload.get('month'))
        year = int(payload.get('year'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Érvénytelen JSON lekérdezés, a dátum mezők hiányoznak vagy érvénytelenek'}, status=400)
    except PermissionDenied:
        return JsonResponse({'error': 'Nincs jogosultságod a dátum lekéréséhez'}, status=403)
    except DatabaseError:
        return JsonResponse({'error': 'Adatbázis hiba történt JSON mezőben dátum lekérésekor'}, status=500)

    target_date = date(year, month, day)
    if target_date < date.today():
        return JsonResponse({'error': 'Nem módosíthatsz múltbeli dátumokat'}, status=400)
    emp_req = EmployeeRequests.objects.filter(employee=request.user.employee, year=year, month=month).first()
    if not emp_req:
        return JsonResponse({'error': 'Nincs műszak igényed ehhez a hónaphoz'}, status=404)
    with transaction.atomic():
        try:
            emp_req = EmployeeRequests.objects.select_for_update().get(pk=emp_req.pk)
        except DatabaseError:
            return JsonResponse({'error': 'Adatbázis hiba történt a műszak igény zárolásakor'}, status=500)
    emp_req.request_data[str(day)] = 'green' if emp_req.request_data.get(str(day)) == 'red' else 'red'
    emp_req.save()

    return JsonResponse({'status': 'ok', 'day': day, 'color': emp_req.request_data[str(day)]})
