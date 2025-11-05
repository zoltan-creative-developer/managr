# # scripts/normalize_staff_schedules.py
# from apps.models import StaffSchedules

# count = 0
# for s in StaffSchedules.objects.all():
#     sd = s.schedule_data
#     changed = False

#     # listából dict eset (legacy)
#     if isinstance(sd, list) and len(sd) > 0 and isinstance(sd[0], dict):
#         sd = sd[0]
#         changed = True

#     # ha nem dict, hozzunk létre üreset
#     if not isinstance(sd, dict):
#         sd = {}
#         changed = True

#     # napértékek normalizálása
#     for day, val in list(sd.items()):
#         if not isinstance(val, list):
#             sd[day] = [val if isinstance(val, str) else 'red', val if isinstance(val, str) else 'red']
#             changed = True
#         elif len(sd[day]) < 2:
#             sd[day] = (sd[day] + ['red','red'])[:2]
#             changed = True

#     if changed:
#         s.schedule_data = sd
#         s.save()
#         print("normalized", s.pk)
#         count += 1

# print("done, normalized:", count)




# # python manage.py shell
# from apps.models import StaffSchedules
# bad = []
# for s in StaffSchedules.objects.all():
#     sd = s.schedule_data
#     if isinstance(sd, dict):
#         for day, val in sd.items():
#             if isinstance(val, list) and len(val) == 2 and all(x == 'n' for x in val):
#                 bad.append((s.pk, getattr(s, 'employee_id', None), day, val))
#     elif isinstance(sd, list):
#         # legacy list case: inspect first element if it's a dict
#         if len(sd) > 0 and isinstance(sd[0], dict):
#             for day, val in sd[0].items():
#                 if isinstance(val, list) and len(val) == 2 and all(x == 'n' for x in val):
#                     bad.append((s.pk, getattr(s, 'employee_id', None), day, val))
# print('found', len(bad), 'matches')
# for item in bad[:50]:
#     print(item)

import traceback
from apps.models import StaffSchedules
from django.db import transaction, IntegrityError

def delete_staff_schedule(employee_id):
    obj = None
    with transaction.atomic():
        try:
            print(f"Deleting StaffSchedules for employee_id: {employee_id}")
            # delete() returns a tuple: (num_deleted, { 'app.Model': n, ... })
            obj = StaffSchedules.objects.filter(employee_id=employee_id).delete()
        except IntegrityError:
            obj = None
            print(f"IntegrityError occurred during deletion of schedule: {employee_id}")
            print(traceback.format_exc())
    return obj

delete_staff_schedule(8)

# for emp_id in range(4, 9):
#     delete_staff_schedule(emp_id)