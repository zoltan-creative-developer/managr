import traceback
from apps.models import StaffSchedules
from django.db import transaction, IntegrityError

def delete_all_staff_schedules():
    with transaction.atomic():
        try:
            obj, deleted = StaffSchedules.objects.all().delete()
            print(f"Deleted {deleted} staff schedules.")
        except IntegrityError:
            obj = None
            print("IntegrityError occurred during unregistration of all accounts.")
            print(traceback.format_exc())
    return obj

def bulk_delete_staff_schedules():
    with transaction.atomic():
        try:
            employee_ids_to_delete = [
                2,
                3,
                4,
            ]
            obj, deleted = StaffSchedules.objects.filter(id__in=employee_ids_to_delete).delete()
            print(f"Deleted {deleted} staff schedules.")
        except IntegrityError:
            obj = None
            print("IntegrityError occurred during bulk unregistration.")
            print(traceback.format_exc())
    return obj

def delete_specific_staff_schedule(staff_schedule_id):
    with transaction.atomic():
        try:
            obj, deleted = StaffSchedules.objects.filter(id=staff_schedule_id).delete()
            print(f"Deleted {deleted} staff schedules.")
        except IntegrityError:
            obj = None
            print(f"IntegrityError occurred during unregistration of account: {staff_schedule_id}")
            print(traceback.format_exc())
    return obj