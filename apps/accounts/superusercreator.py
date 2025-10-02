from apps.models import CustomUser

CustomUser.objects.create_superuser(
    email='admin.etterembeosztas@napfenyes.hu',
    password='etteremadmin1999',
    first_name='Admin',
    last_name='User'
)