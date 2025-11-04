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
        except Exception:
            user = None
            print("An unexpected error occurred during registration of new account.")
            print(traceback.format_exc())
    return user

def bulk_register_users(start=1, num=1):
    registered_users = []
    user_data_list = [
        {
            'email': f'user{i}@example.com',
            'password': f'password{i}',
            'first_name': f'First{i}',
            'last_name': f'Last{i}',
        }
        for i in range(start, start + num)
    ]

    with transaction.atomic():
        for user_data in user_data_list:
            try:
                user = get_user_model().objects.create_user(
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                )
                registered_users.append(user)
            except IntegrityError:
                print(f"IntegrityError occurred during registration of account: {user_data['email']}")
                print(traceback.format_exc())
            except Exception:
                print(f"An unexpected error occurred during registration of account: {user_data['email']}")
                print(traceback.format_exc())
    return registered_users