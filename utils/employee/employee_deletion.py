import traceback
from apps.models import Employee
from django.db import transaction, IntegrityError

def delete_all_employees():
    with transaction.atomic():
        try:
            Employee.objects.all().delete()
        except IntegrityError:
            obj = None
            print("IntegrityError occurred during unregistration of all accounts.")
            print(traceback.format_exc())
    return obj

def bulk_delete_employees():
    with transaction.atomic():
        try:
            employee_ids_to_delete = [
                2,
                3,
                4,
            ]
            obj, deleted = Employee.objects.filter(id__in=employee_ids_to_delete).delete()
        except IntegrityError:
            obj = None
            print("IntegrityError occurred during bulk unregistration.")
            print(traceback.format_exc())
    return obj

def unregister_specific_account(employee_id):
    obj = None
    with transaction.atomic():
        try:
            obj = Employee.objects.filter(id=employee_id).delete()
        except IntegrityError:
            obj = None
            print(f"IntegrityError occurred during unregistration of account: {employee_id}")
            print(traceback.format_exc())
    return obj