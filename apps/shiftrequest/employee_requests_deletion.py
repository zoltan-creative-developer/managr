from apps.models import EmployeeRequests

def delete_employee_requests():
    deleted, _ = EmployeeRequests.objects.filter(employee=1).delete()
    print(f"{deleted} bejegyzés törölve.")
delete_employee_requests()