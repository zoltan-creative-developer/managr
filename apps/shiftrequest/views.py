import calendar
from urllib import request
from django.shortcuts import render, redirect

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
    EmployeeRequests,
    DayCell,
    EmployeePreference,
    ScheduleStatistics,
)

from django.http import JsonResponse, HttpResponseBadRequest
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from datetime import datetime, date, timedelta

@staff_member_required
def management_shift_request_view(request):
    """Custom shift request view that renders the management-shift-request.html template"""
    context = {
        'title': 'Shift Request',
        'welcome_message': 'Welcome to the shift request page.',
    }
    return render(request, 'apps/shiftrequest/templates/management-shift-request.html', context)

def employee_shift_request_view(request):
    # if not MonthlySchedule.objects.first():
    #     schedule = MonthlySchedule.objects.create(
    #         year=datetime.now().year,
    #         month=datetime.now().month,
    #         name=str(datetime.now().year) + datetime.now().month_name[datetime.now().month] + 'i műszakbeosztás',
    #         description=str(datetime.now().year) + ' ' + datetime.now().month_name[datetime.now().month] + 'i műszakbeosztás',
    #         created_by=request.user,
    #         status='draft',  # vagy 'in_review', 'approved', stb.
    #     )
    # else:
    #     schedule = MonthlySchedule.objects.filter(year=2025, month=10).first()

    __year = datetime.now().year
    __month = datetime.now().month
    days_in_month = calendar.monthrange(__year, __month)[1]
    days = [day for day in range(1, days_in_month + 1)]
    week_lengths = [calendar.weekday(__year, __month, day) for day in days]
    first_weekday = calendar.monthrange(__year, __month)[0]  # Hónap első napjának a hét napja (0=Hétfő, 6=Vasárnap)
    last_weekday = calendar.monthrange(__year, __month)[1]  # Hónap utolsó napjának a hét napja (0=Hétfő, 6=Vasárnap)
    total_weeks = (days_in_month + first_weekday) // 7 + 1
    weeks = [i for i in range(1, total_weeks + 1)]
    ordered_days = []
    for i in range(total_weeks):
        if i == 0:
            ordered_days.append([''] * first_weekday + days[:7 - first_weekday])
        else:
            ordered_days.append(days[7 - first_weekday + (i - 1) * 7: 7 - first_weekday + i * 7])

    emp = Employee.objects.filter(user=request.user).first()
    if not EmployeeRequests.objects.filter(employee=emp).first():
        emp_req = EmployeeRequests.objects.create(
            employee=emp,
            year=datetime.now().year,
            month=datetime.now().month,
            request_data={'availability': {day: 'green' for day in range(1, days_in_month + 1)}}
        )
    else:
        emp_req = EmployeeRequests.objects.filter(employee=emp).first()

    emp_req.save()
    messages.success(request, 'Your preferences have been updated successfully.')

    html_table = generate_html_table(ordered_days)

    context = {
        'error_message': 'Nincs elérhető beosztás. Kérjük, hozzon létre egyet a management parancsokkal.',
        'html_table': html_table,
    }

    return render(request, 'shiftrequest/employee-shift-request.html', context)

def generate_html_table(ordered_days):
    html = '''<div class="table-responsive">
        <table class="table table-bordered align-middle shift-calendar-table">'''

    html += '''<thead>
    <tr>'''

    for i in range(7):
        html += f'<th class="header-cell"><div class="cell-inner">{calendar.day_name[i][0:2]}</div></th>'

    html += '''</tr>
    </thead>
    <tbody>'''

    for i in range(len(ordered_days)):
        html += '<tr>'
        for day in ordered_days[i]:
            if day:
                html += f'<td class="available-cell"><div class="cell-inner">{day}</div></td>'
            else:
                html += '<td><div class="cell-inner"></div></td>'
        html += '</tr>'
    html += '</tbody></table></div>'
    return html


@ensure_csrf_cookie
def show_calendar(request, year, month):
    """
    Rendereli az október hónap heteit soronként. Üres cellák 0 helyére jelennek meg.
    """
    __year = year
    __month = month
    weeks = calendar.monthcalendar(__year, __month)  # minden hét: lista 7 elemmel, 0 ha nincs nap

    # lekérdezzük a napok színét (ha mentjük)
    day_colors = {}
    emp = Employee.objects.get(user=request.user)
    emp_req = EmployeeRequests.objects.filter(employee=emp, year=__year, month=__month).first()
    if emp_req and "availability" in emp_req.request_data:
        for day in range(1, calendar.monthrange(__year, __month)[1] + 1):
            color = emp_req.request_data["availability"].get(str(day)) or emp_req.request_data["availability"].get(day)
            if color:
                day_colors[day] = color
    else:
        for day in range(1, calendar.monthrange(__year, __month)[1] + 1):
            day_colors[day] = 'green'
    print(day_colors)
    context = {
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




def get_employee_shift_requests(request, employee_id):
    # """Fetch shift requests for a specific employee"""
    # employee = get_object_or_404(Employee, id=employee_id)
    # return JsonResponse(list(shift_requests), safe=False)

    if request.method == 'POST':
            # Itt dolgozd fel a kérést
            return redirect('sikeres_oldal')  # vagy render(...)
    return render(request, 'sablon.html')


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

