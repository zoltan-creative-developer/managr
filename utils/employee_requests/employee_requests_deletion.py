import traceback
from apps.models import EmployeeRequests
from django.db import transaction, IntegrityError

def delete_all_employee_requests():
    with transaction.atomic():
        try:
            obj, deleted = EmployeeRequests.objects.all().delete()
            print(f"Deleted {deleted} employee requests.")
        except IntegrityError:
            obj = None
            print("IntegrityError occurred during unregistration of all accounts.")
            print(traceback.format_exc())
    return obj

def bulk_delete_employee_requests():
    with transaction.atomic():
        try:
            employee_ids_to_delete = [
                2,
                3,
                4,
            ]
            obj, deleted = EmployeeRequests.objects.filter(id__in=employee_ids_to_delete).delete()
            print(f"Deleted {deleted} employee requests.")
        except IntegrityError:
            obj = None
            print("IntegrityError occurred during bulk unregistration.")
            print(traceback.format_exc())
    return obj

def delete_specific_request(employee_request_id):
    with transaction.atomic():
        try:
            obj, deleted = EmployeeRequests.objects.filter(id=employee_request_id).delete()
            print(f"Deleted {deleted} employee requests.")
        except IntegrityError:
            obj = None
            print(f"IntegrityError occurred during unregistration of account: {employee_request_id}")
            print(traceback.format_exc())
    return obj