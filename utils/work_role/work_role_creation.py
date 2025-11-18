import traceback
from apps.models import WorkArea, WorkRole
from django.db import transaction

error_message = ""

def create_work_role():
    with transaction.atomic():
        try:
            for i in range(len(WorkRole.ROLE_CHOICES)):
                if not WorkRole.objects.filter(code=WorkRole.ROLE_CHOICES[i][0]).exists():
                    obj, created = WorkRole.objects.update_or_create(
                        code=WorkRole.ROLE_CHOICES[i][0],
                        defaults={
                            'name': WorkRole.ROLE_CHOICES[i][1],
                            'description': f'Default description for {WorkRole.ROLE_CHOICES[i][1]}',
                            'hourly_rate': 0,
                            'is_active': True,
                        }
                    )
                    work_role = obj
        except Exception:
            work_role = None
            print("An unexpected error occurred during creation of WorkRole.")
            print(traceback.format_exc())
    return work_role