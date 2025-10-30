from apps.models import WorkArea

def delete_test_area():
    WorkArea.objects.filter(code='test_area').delete()
