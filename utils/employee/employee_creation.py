import traceback
from apps.models import Employee, EmploymentType
from django.db import transaction, IntegrityError
from datetime import date, datetime

error_massage = ""
__year = date(datetime.year)
__month = date(datetime.month)

if not Employee.objects.filter(user=1).exists():
    with transaction.atomic():
        try:
            obj, created = Employee.objects.update_or_create(
                user=1,
                birth_date=date(2000, 1, 1),
                gender="F",
                phone_number="0036xx1234567",
                address="Teszt utca 1, Teszt város, 1234",

                hire_date=date(__year, __month, 1),
                employment_type=EmploymentType.objects.filter(code="teljes_munkaidos").first(),
                min_full_shifts_per_month=10,
                max_hours_per_day=12,
                max_full_shifts_per_week=5
            )
            emp = obj
        except IntegrityError:
            user = None
            print(f"IntegrityError occurred during creation of new employee: {user.full_name}")
            print(traceback.format_exc())
else:
    print("IntegrityError occurred during creation of new employee.")
