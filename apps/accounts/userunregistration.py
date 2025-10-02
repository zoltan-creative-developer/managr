from django.contrib.auth import get_user_model

def unregister_account():
    User = get_user_model()
    User.objects.filter(email='testuser1@example.com').delete()