import traceback
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError

def unregister_all_accounts():
    with transaction.atomic():
        try:
            User = get_user_model()
            User.objects.all().delete()
        except IntegrityError:
            obj = None
            print("IntegrityError occurred during unregistration of all accounts.")
            print(traceback.format_exc())
    return obj

def bulk_unregister_accounts():
    with transaction.atomic():
        try:
            User = get_user_model()
            user_ids_to_delete = [
                1,
                2,
                3,
            ]
            obj, deleted = User.objects.filter(id__in=user_ids_to_delete).delete()
        except IntegrityError:
            obj = None
            print("IntegrityError occurred during bulk unregistration.")
            print(traceback.format_exc())
    return obj

def unregister_specific_account(user_id):
    with transaction.atomic():
        try:
            User = get_user_model()
            User.objects.filter(id=user_id).delete()
        except IntegrityError:
            obj = None
            print(f"IntegrityError occurred during unregistration of account: {user_id}")
            print(traceback.format_exc())
    return obj