import os, getpass
import traceback
from django.db import transaction, IntegrityError
from apps.models import CustomUserManager
from django.contrib.auth import get_user_model

def create_superuser():
    User = get_user_model()
    try:
        with transaction.atomic():
            pwd=os.environ.get('DJANGO_SUPERUSER_PASSWORD')
            if not pwd:
                raise ValueError("Kell egy jelszó a superuser létrehozásához.")
            user = User.objects.create_superuser(
                email='admin@example.com',
                password=pwd,
                first_name='Admin',
                last_name='User'
            )
    except IntegrityError:
        user = None
        print("IntegrityError occurred during superuser creation.")
        print(traceback.format_exc())
    except Exception as e:
        user = None
        print(f"An error occurred during superuser creation: {e}")
        print(traceback.format_exc())
    return user