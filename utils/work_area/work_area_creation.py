import traceback
from apps.models import WorkArea
from django.db import transaction

error_message = ""

def create_work_area():
    with transaction.atomic():
        try:
            for i in range(len(WorkArea.AREA_CHOICES)):
                if not WorkArea.objects.filter(code=WorkArea.AREA_CHOICES[i][0]).exists():
                    obj, created = WorkArea.objects.update_or_create(
                        code=WorkArea.AREA_CHOICES[i][0],
                        defaults={
                            'name': WorkArea.AREA_CHOICES[i][1],
                            'description': f'Default description for {WorkArea.AREA_CHOICES[i][1]}',
                            'is_active': True
                        }
                    )
                    work_area = obj
        except Exception:
            work_area = None
            print("An unexpected error occurred during creation of WorkArea.")
            print(traceback.format_exc())
    return work_area