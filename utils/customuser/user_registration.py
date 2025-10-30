import traceback
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError

def register_new_account():
    User = get_user_model()

    with transaction.atomic():
        try:
            user = User.objects.create_user(
                email='szantozsolt@example.com',
                password='etteremszantozsolt123',
                first_name='Zsolt',
                last_name='Szántó',
            )
        except IntegrityError:
            user = None
            print("IntegrityError occurred during registration of new account.")
            print(traceback.format_exc())
    return user
