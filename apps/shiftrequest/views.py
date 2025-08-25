from django.shortcuts import render

def management_shift_request_view(request):
    """Custom shift request view that renders the management-shift-request.html template"""
    context = {
        'title': 'Shift Request',
        'welcome_message': 'Welcome to the shift request page.',
    }
    return render(request, 'apps/shiftrequest/templates/management-shift-request.html', context)