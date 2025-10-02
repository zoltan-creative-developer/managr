from apps.models import CustomUserManager, CustomUser, Employee, WorkArea, ShiftType, MonthlySchedule
from django.contrib.auth import get_user_model

def register_new_account():
    User = get_user_model()
    for i in range(1, 100):
        user = User.objects.create_user(email='testuser' + str(i) + '@example.com', password='testpass')
        work_area = WorkArea.objects.create(code='test_area' + str(i), name='Test Area')
        employee = Employee.objects.create(
            user=user,
            employee_id='E000' + str(i),
            hire_date='2025-01-01',
            primary_work_area=work_area
        )
    employee.work_roles.set([]) # Set roles if needed

    # # Create shift types
    # shift_types = {}
    # for code, name, short in [(0, 'Szabadnap', 'sz'), 
    #                             (1, 'Délelőtt', 'de'),
    #                             (10, 'Delután', 'du'),
    #                             (11, 'Egész nap', 'h')
    # ]:
    #     st = ShiftType.objects.create(code=code, name=name, short_name=short)
    #     shift_types[code] = st

    # # Create a schedule
    # schedule = MonthlySchedule.objects.create(
    #     year=2025, month=10, name='Test Schedule', description='Test'
    # )
