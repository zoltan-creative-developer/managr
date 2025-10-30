from apps.models import Employee, EmployeeRequests, StaffSchedules, ScheduleDayCell

Employee.objects.all().delete()
EmployeeRequests.objects.all().delete()
StaffSchedules.objects.all().delete()
ScheduleDayCell.objects.all().delete()