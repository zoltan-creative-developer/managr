import traceback
from django.db import transaction, IntegrityError
from apps.models import CustomUserManager

def create_superuser():
    try:
        with transaction.atomic():
            obj, created = CustomUserManager.create_superuser(
                email='admin.etterembeosztas@napfenyes.hu',
                password='etteremadmin1999',
                first_name='Admin',
                last_name='User'
            )
    except IntegrityError:
        obj = None
        print("IntegrityError occurred during superuser creation.")
        print(traceback.format_exc())
    return obj