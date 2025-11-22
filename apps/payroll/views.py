from django.shortcuts import render

def management_payroll_view(request):
    

    context = {
        'title': 'Payroll',
        'welcome_message': 'Welcome to the payroll page.',
    }
    return render(request, 'apps/payroll/templates/management-payroll.html', context)
