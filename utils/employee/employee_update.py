from django.contrib.auth import get_user_model
import traceback
from apps.models import AbsenceType, Employee, EmploymentType, WorkRole
from django.db import transaction
from datetime import date

error_message = ""
__year = date.today().year
__month = date.today().month

def update_employee():
    with transaction.atomic():
        try:
            employee = Employee.objects.select_for_update().get(pk=1)
            # employee.birth_date=date(2000, 1, 1),
            # employee.gender="F",
            # employee.phone_number="0036xx1234567",
            # employee.address="Teszt utca 1, Teszt város, 1234",

            # employee.hire_date=date(__year, __month, 1),
            # employee.employment_type="teljes_munkaidos",
            # employee.absence_type=None,
            employee.default_work_role=WorkRole.objects.filter(code='fopincer').first()
            # employee.min_full_shifts_per_month=10,
            # employee.max_hours_per_day=12,
            # employee.max_full_shifts_per_week=5
            employee.save()
        except Exception:
            employee = None
            print("An unexpected error occurred during registration of new account.")
            print(traceback.format_exc())
    return employee