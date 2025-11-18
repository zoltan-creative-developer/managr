import traceback
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError

def modify_account():
    User = get_user_model()

    with transaction.atomic():
        try:
            user = User.objects.select_for_update().get(id=11)
            user.last_name = 'Harmadik'
            user.first_name = 'Diáklány'
            user.save()
        except Exception:
            user = None
            print("An unexpected error occurred during registration of new account.")
            print(traceback.format_exc())
    return user