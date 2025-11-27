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
    EmploymentType,
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

    # Beosztás tábla színek meghatározása:
    #
    # ha van már beosztás tábla
    # -> ha be lett osztva olyan napra, amikor ráér, vagy nem adott le igény, akkor narancs
    # -> ha be lett osztva olyan napra, amikor nem ér rá, akkor halványnarancs
    
    # -> ha nem lett beosztva egy napra, akkor halvány halványkék (betegszabadság), 
    # halványsárga (fizetett/nem fizetett szabadságigény), 
    # halványzöld (munkatársi vagy egyéb közösségi elfoglaltság) vagy 
    # barackszín (nincs szabadságigény) az igény alapján

    # ha még nincs beosztás tábla
    # akkor minde nap olyan színű mint amikor nincs beosztva egy adott napra 

 
    for employee in employee_qs:
        request_colors = {}
        colors = {}
        for day in day_list:
            if not employee_requests.filter(employee=employee, year=__year, month=__month).exists():
                request_colors[day] = ['peachpuff', 'peachpuff']
            else:
                req = employee_requests.get(employee=employee, year=__year, month=__month).request_data
                v = req.get(day)
                if v == 'blue':
                    request_colors[day] = ['lightblue', 'lightblue']
                elif v == 'yellow':
                    request_colors[day] = ['lightyellow', 'lightyellow']
                elif v == 'green':
                    request_colors[day] = ['lightgreen', 'lightgreen']
                else:
                    request_colors[day] = ['peachpuff', 'peachpuff']

        if not StaffSchedules.objects.filter(employee=employee, year=__year, month=__month).exists():
            try:
                with transaction.atomic():
                    obj, created = StaffSchedules.objects.update_or_create(
                        employee=employee, year=__year, month=__month,
                        defaults={'schedule_data': request_colors}
                    )
                    print(f"Created new StaffSchedules for employee id {employee.id}: {obj.schedule_data}")
            except IntegrityError:
                obj = StaffSchedules.objects.get(employee=employee, year=__year, month=__month)
            schedule_colors = obj.schedule_data
        else:
            obj = StaffSchedules.objects.get(employee=employee, year=__year, month=__month)
            schedule_colors = obj.schedule_data
            for day in day_list:
                if schedule_colors[day] == ['orange', 'orange'] and request_colors[day] != ['peachpuff', 'peachpuff']:
                    schedule_colors[day] = request_colors[day]
        colors = schedule_colors
        day_shift_colors[employee.id] = colors

    employee_map = {emp.id: emp for emp in employee_qs}
    role_order = {code: idx for idx, (code, _) in enumerate(WorkRole.ROLE_CHOICES)}
    def _sort_key(item):
        emp_id, _ = item
        emp = employee_map.get(emp_id)
        if not emp or not getattr(emp.default_work_role, 'code', None):
            return (len(role_order), emp_id)
        return (role_order.get(emp.default_work_role.code, len(role_order)), emp_id)
    day_shift_colors = dict(sorted(day_shift_colors.items(), key=_sort_key))

    fopincer_emps = list(employee_qs.filter(default_work_role__code='fopincer').values_list('id', flat=True))
    elso_kasszas_emps = list(employee_qs.filter(default_work_role__code='elso_kasszas').values_list('id', flat=True))
    felszolgalo_emps = list(employee_qs.filter(default_work_role__code='felszolgalo').values_list('id', flat=True))
    tobbi_poszt_emps = list(employee_qs.exclude(default_work_role__code__in=['fopincer', 'elso_kasszas', 'felszolgalo']).values_list('id', flat=True))

    fopincer_sums= {}
    elso_kasszas_sums= {}
    felszolgalo_sums= {}
    tobbi_sums= {}
    for day in day_list:
        for i in range(2):
            count_fopincer = sum([1 if day_shift_colors[emp_id][day][i] in ('orange', 'lightorange') else 0 for emp_id in fopincer_emps])
            fopincer_sums.setdefault(day, [0,0])[i] = 1-count_fopincer
            count_elso_kasszas = sum([1 if day_shift_colors[emp_id][day][i] in ('orange', 'lightorange') else 0 for emp_id in elso_kasszas_emps])
            elso_kasszas_sums.setdefault(day, [0,0])[i] = count_elso_kasszas
            count_felszolgalo = sum([1 if day_shift_colors[emp_id][day][i] in ('orange', 'lightorange') else 0 for emp_id in felszolgalo_emps])
            felszolgalo_sums.setdefault(day, [0,0])[i] = count_felszolgalo
            count_tobbi = sum([1 if day_shift_colors[emp_id][day][i] in ('orange', 'lightorange') else 0 for emp_id in tobbi_poszt_emps])
            tobbi_sums.setdefault(day, [0,0])[i] = count_tobbi

    male_emps = list(employee_qs.filter(gender='male').values_list('id', flat=True))
    temporary_male_emps = list(employee_qs.filter(gender='male', employment_type__code='temporary').values_list('id', flat=True))
    female_emps = list(employee_qs.filter(gender='female').values_list('id', flat=True))
    temporary_female_emps = list(employee_qs.filter(gender='female', employment_type__code='temporary').values_list('id', flat=True))
    temporary_male_sums= {}
    temporary_female_sums= {}
    for day in day_list:
        for i in range(2):
            count_male = sum([1 if day_shift_colors[emp_id][day][i] in ('orange', 'lightorange') else 0 for emp_id in temporary_male_emps])
            temporary_male_sums.setdefault(day, [0,0])[i] = 1-count_male
            count_female = sum([1 if day_shift_colors[emp_id][day][i] in ('orange', 'lightorange') else 0 for emp_id in temporary_female_emps])
            temporary_female_sums.setdefault(day, [0,0])[i] = 1-count_female

    emp_sums = {}
    for emp, shifts in day_shift_colors.items():
        emp_sum = sum([1 if shifts[day][i] in ('orange', 'lightorange') else 0 for day in day_list for i in range(2)])
        emp_sums[emp] = emp_sum
    employee_sums = dict(sorted(emp_sums.items(), key=_sort_key))

    min_shifts = {}
    for employee in employee_qs:
        min_shifts[employee.id] = employee.min_full_shifts_per_month
    min_shifts = dict(sorted(min_shifts.items(), key=_sort_key))

    shifts_left = {}
    for emp_id in employee_sums.keys():
        shifts_left[emp_id] = min_shifts.get(emp_id, 0) - employee_sums.get(emp_id, 0)
    shifts_left = dict(sorted(shifts_left.items(), key=_sort_key))
        
    daytime_aggregates = calculate_aggregated_values(__year, __month)

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
        'days_of_the_week': ['H', 'K', 'Sze', 'Cs', 'P', 'Szo', 'V'],
        'days_of_week_in_month': [
            hu_day_map3.get(calendar.day_name[calendar.weekday(__year, __month, day)], '') 
            for day in range(1, calendar.monthrange(__year, __month)[1] + 1)
        ],
        'weekend_days': [day for day in day_list if calendar.weekday(__year, __month, int(day)) >= 5],
        'weekend_days_of_week': ['Szo', 'V'],

        'employee_names': {emp.id: " ".join([emp.user.last_name, emp.user.first_name]) for emp in employee_qs},
        'day_shift_colors': day_shift_colors,
        'fopincer_emps': fopincer_emps,
        'elso_kasszas_emps': elso_kasszas_emps,
        'felszolgalo_emps': felszolgalo_emps,
        'tobbi_poszt_emps': tobbi_poszt_emps,
        'fopincer_sums': fopincer_sums,
        'elso_kasszas_sums': elso_kasszas_sums,
        'felszolgalo_sums': felszolgalo_sums,
        'tobbi_sums': tobbi_sums,
        'temporary_male_sums': temporary_male_sums,
        'temporary_female_sums': temporary_female_sums,
        'employee_sums': employee_sums,
        'min_shifts': min_shifts,
        'shifts_left': shifts_left,
        'daytime_aggregates': daytime_aggregates,
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
                dayval = ['peachpuff', 'peachpuff']

        # Ensure at least two elements
        if len(dayval) < 2:
            dayval = (dayval + ['peachpuff', 'peachpuff'])[:2]
        # Toggle
        try:
            if dayval[shift] not in ['orange', 'lightorange']:
                dayval[shift] = 'orange' if dayval[shift] == 'peachpuff' else 'lightorange'
            elif EmployeeRequests.objects.filter(employee=emp, year=year, month=month).first() != None:
                if EmployeeRequests.objects.get(employee=emp, year=year, month=month).request_data.get(str(day)) == 'peachpuff':
                    dayval[shift] = 'peachpuff'
                else:
                    dayval[shift] = 'light' + EmployeeRequests.objects.get(employee=emp, year=year, month=month).request_data.get(str(day))
            else:
                dayval[shift] = 'peachpuff'

        except Exception:
            return JsonResponse({'error': 'Hiba a nap értékének módosításakor'}, status=500)

        sd[day_key] = dayval
        schedule.schedule_data = sd
        try:
            schedule.save()
        except DatabaseError:
            return JsonResponse({'error': 'Adatbázis hiba mentéskor'}, status=500)
    return JsonResponse({'status': 'ok', 'day': day, 'color': schedule.schedule_data[str(day)][shift]})


def calculate_aggregated_values(year, month):
    __year = year
    __month = month
    day_list = [str(d) for d in range(1, calendar.monthrange(__year, __month)[1] + 1)]
    schedule_qs = StaffSchedules.objects.filter(year=year, month=month)
    daytime_aggregates = {}
    for day in day_list:
        shift_total = [0,0]
        for schedule in schedule_qs:
            shift_total[0] = shift_total[0] + 1 if schedule.schedule_data[day][0] in ('orange', 'lightorange') else shift_total[0]
            shift_total[1] = shift_total[1] + 1 if schedule.schedule_data[day][1] in ('orange', 'lightorange') else shift_total[1]
        daytime_aggregates[day] = (3-shift_total[0], 3-shift_total[1])
    return daytime_aggregates