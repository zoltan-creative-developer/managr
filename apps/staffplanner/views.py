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
def set_staffplanner_dates(request):
    year = request.POST.get('year') if request.POST.get('year') else date.today().year
    month = request.POST.get('month') if request.POST.get('month') else date.today().month
    year = int(year)
    month = int(month)
    request.session['staffplanner_year'] = year
    request.session['staffplanner_month'] = month
    return redirect('management_headcount_planning', year=year, month=month)

@staff_member_required
def management_headcount_planning_view(request, year, month):
    __year = year
    __month = month
    days_of_the_week = ['Hétfő', 'Kedd', 'Szerda', 'Csütörtök', 'Péntek', 'Szombat', 'Vasárnap']
    days_of_the_week3 = ['H', 'K', 'Sze', 'Cs', 'P', 'Szo', 'V']
    weekend_days_of_the_week = ['Szombat', 'Vasárnap']
    weekend_days_of_the_week3 = ['Szo', 'V']
    first_week_index_of_the_year_in_the_month = date(__year, __month, 1).isocalendar()[1]    
    day_list = [str(d) for d in range(1, calendar.monthrange(__year, __month)[1] + 1)]
    hu_day_map = {'Monday':'Hétfő','Tuesday':'Kedd','Wednesday':'Szerda','Thursday':'Csütörtök','Friday':'Péntek','Saturday':'Szombat','Sunday':'Vasárnap'}
    hu_day_map3 = {'Monday':'H','Tuesday':'K','Wednesday':'Sze','Thursday':'Cs','Friday':'P','Saturday':'Szo','Sunday':'V'}
    days_of_week_in_month = [
    hu_day_map3.get(calendar.day_name[calendar.weekday(__year, __month, day)], '') 
    for day in range(1, calendar.monthrange(__year, __month)[1] + 1)
    ]
    weeks = {i: val for i, val in enumerate(calendar.monthcalendar(__year, __month))} # elements of weeks:
    # {0: [0, 0, 1, 2, 3, 4, 5], 1: [6, 7, 8, 9, 10, 11, 12], ...}
    days_of_week_in_month_sliced_per_week = {
        i: [hu_day_map3.get(calendar.day_name[calendar.weekday(__year, __month, day)], '')
            for day in week if day != 0]
        for i, week in weeks.items()
    }
    employee_qs = Employee.objects.filter(user__is_active=True)
    employee_names = {emp.id: " ".join([emp.user.last_name, emp.user.first_name]) for emp in employee_qs}
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

    emp_hour_values = {}
    for emp_id, shifts in day_shift_colors.items():
        per_day = {}
        for day in day_list:
            day_hours = 0
            for i in range(2):
                if shifts[day][i] in ('orange', 'lightorange'):
                    day_hours += 5.5  # assuming each shift is 5.5 hours
            per_day[day] = day_hours
        emp_hour_values[emp_id] = per_day
    employee_hour_values = dict(sorted(emp_hour_values.items(), key=_sort_key))

    day_employee_assignments = {}
    for day in day_list:
        assigned_emps = {0: [], 1: []}
        for i in range(2):
            shift_assigned_emps = [
                employee_names[emp_id]
                for emp_id, shifts in day_shift_colors.items()
                if shifts.get(day, ['', ''])[i] in ('orange', 'lightorange')
            ]
            assigned_emps[i] = shift_assigned_emps
        day_employee_assignments[day] = assigned_emps

    work_area_assignments = {}
    for work_role_code, _ in WorkRole.ROLE_CHOICES:
        work_area_assignments.setdefault(work_role_code, {})
        for day in day_list:
            assigned_emps = {0: [], 1: []}
            for i in range(2):
                shift_assigned_emps = [
                    employee_names[emp_id]
                    for emp_id, shifts in day_shift_colors.items()
                    if getattr(employee_map.get(emp_id), 'default_work_role', None) and
                    getattr(employee_map[emp_id].default_work_role, 'code', None) == work_role_code
                    and any(shifts.get(day, ['', ''])[i] in ('orange', 'lightorange') for i in range(2))
                ]
                assigned_emps[i] = shift_assigned_emps
            work_area_assignments[work_role_code][day] = assigned_emps
            if work_role_code == 'fopincer':
                print(f"Day {day}, Shift {i}, Assigned fopincers: {assigned_emps[i]}")
 
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
        
    daytime_aggregates, daytime_lacks = calculate_aggregated_values(__year, __month)

    daytime_aggregates_sliced_per_week = {
        i: { str(day): daytime_aggregates.get(str(day), [0, 0]) for day in week if day != 0 }
        for i, week in weeks.items()
    }

    context = {
        'title': 'Létszám tervezés',
        'welcome_message': 'Üdvözlünk a létszám tervezés oldalon!',
        'year': __year,
        'dropdown_year_options': list(range(2020, date.today().year + 1)),
        'month': __month,
        'dropdown_month_options': [
        (1, 'Január'), (2, 'Február'), (3, 'Március'), (4, 'Április'),
        (5, 'Május'), (6, 'Június'), (7, 'Július'), (8, 'Augusztus'),
        (9, 'Szeptember'), (10, 'Október'), (11, 'November'), (12, 'December'),
        ],
        'day_list': day_list,
        'daytime_list': [['de', 'du'] for _ in day_list],
        'days_in_month': calendar.monthrange(__year, __month)[1],
        'month_name': calendar.month_name[__month],
        'weeks': weeks,
        'days_of_the_week': days_of_the_week,
        'days_of_the_week3': days_of_the_week3,
        'hu_day_map3': hu_day_map3,
        'days_of_week_in_month': days_of_week_in_month,
        'days_of_week_in_month_sliced_per_week': days_of_week_in_month_sliced_per_week,
        'weekend_days': [day for day in day_list if calendar.weekday(__year, __month, int(day)) >= 5],
        'weekend_days_of_the_week': weekend_days_of_the_week,
        'weekend_days_of_the_week3': weekend_days_of_the_week3,
        'first_week_index_of_the_year_in_the_month': first_week_index_of_the_year_in_the_month,
        'employee_names': employee_names,
        'day_shift_colors': day_shift_colors,
        'employee_hour_values': employee_hour_values,
        'fopincer_emps': fopincer_emps,
        'fopincer_emp_names': [employee_names[emp_id] for emp_id in fopincer_emps],
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
        'daytime_aggregates_sliced_per_week': daytime_aggregates_sliced_per_week,
        'daytime_lacks': daytime_lacks,
        'day_employee_assignments': day_employee_assignments,
        'work_area_assignments': work_area_assignments,
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
    daytime_lacks = {}
    for day in day_list:
        shift_total = [0,0]
        for schedule in schedule_qs:
            shift_total[0] = shift_total[0] + 1 if schedule.schedule_data[day][0] in ('orange', 'lightorange') else shift_total[0]
            shift_total[1] = shift_total[1] + 1 if schedule.schedule_data[day][1] in ('orange', 'lightorange') else shift_total[1]
        daytime_aggregates[day] = (shift_total[0], shift_total[1])
        daytime_lacks[day] = (max(0, 3 - shift_total[0]), max(0, 3 - shift_total[1]))
    return daytime_aggregates, daytime_lacks