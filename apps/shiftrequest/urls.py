from django.urls import path
from apps.shiftrequest.views import management_shift_request_view

urlpatterns = [
    path('management/shift-request/', management_shift_request_view, name='management_shift_request'),
]