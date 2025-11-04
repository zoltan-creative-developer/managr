from django.contrib.auth import get_user_model
import traceback
from apps.models import Employee, EmploymentType
from django.db import transaction, IntegrityError
from datetime import date


error_message = ""
__year = date.today().year
__month = date.today().month

def create_employee():
    if not Employee.objects.filter(user=1).exists():
        with transaction.atomic():
            try:
                obj, created = Employee.objects.update_or_create(
                    user=get_user_model().objects.get(pk=2),
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


def bulk_create_employees(start=0, num=1):
    registered_user_ids = []
    employee_data_list = []
    for i in range(start, start + num):
        user = get_user_model().objects.filter(pk=i).first()
        if not user:
            continue
        employee_data_list.append({
            'user': user,
            'birth_date': date(2000, 1, 1),
            'gender': "F" if i % 2 == 1 else "N",
            'phone_number': "0036xx1234567",
            'address': "Teszt utca 1, Teszt város, 1234",
            'hire_date': date(__year, __month, 1),
            'employment_type': EmploymentType.objects.filter(code="teljes_munkaidos").first(),
            'min_full_shifts_per_month': 10,
            'max_hours_per_day': 12,
            'max_full_shifts_per_week': 5,
        })
        print(f"Prepared employee data for user: {user.get_full_name()}")

    with transaction.atomic():
        for employee_data in employee_data_list:
            try:
                employee = Employee.objects.create(
                    user=employee_data['user'],
                    birth_date=employee_data['birth_date'],
                    gender=employee_data['gender'],
                    phone_number=employee_data['phone_number'],
                    address=employee_data['address'],
                    hire_date=employee_data['hire_date'],
                    employment_type=employee_data['employment_type'],
                    min_full_shifts_per_month=employee_data['min_full_shifts_per_month'],
                    max_hours_per_day=employee_data['max_hours_per_day'],
                    max_full_shifts_per_week=employee_data['max_full_shifts_per_week'],
                )
                registered_user_ids.append(employee.user.id)
            except IntegrityError:
                print(f"IntegrityError occurred during creation of employee: {employee_data['user'].get_full_name}")
                print(traceback.format_exc())
            except Exception:
                print(f"An unexpected error occurred during creation of employee: {employee_data['user'].get_full_name}")
                print(traceback.format_exc())
    return registered_user_ids
