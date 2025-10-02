from django.test import TestCase
from apps.models import CustomUserManager, CustomUser, Employee, WorkArea, ShiftType, MonthlySchedule
from django.contrib.auth import get_user_model

class TestRegisterNewAccount(TestCase):
    def test_setUp(self):
        User = get_user_model()
        user = User.objects.create_user(email='testuser@example.com', password='testpass')
        work_area = WorkArea.objects.create(code='test_area', name='Test Area')
        self.employee = Employee.objects.create(
            user=user,
            employee_id='E001',
            hire_date='2025-01-01',
            primary_work_area=work_area
        )
        self.employee.work_roles.set([]) # Set roles if needed

        # Create shift types
        self.shift_types = {}
        for code, name, short in [(0, 'Szabadnap', 'sz'), 
                                  (1, 'Délelőtt', 'de'),
                                  (10, 'Delután', 'du'),
                                  (11, 'Egész nap', 'h')
        ]:
            st = ShiftType.objects.create(code=code, name=name, short_name=short)
            self.shift_types[code] = st

        # Create a schedule
        self.schedule = MonthlySchedule.objects.create(
            year=2025, month = 7, name='Test Schedule', description='Test'
        )
