from django.shortcuts import render

def management_headcount_planning_view(request):
    """Custom headcount planning view that renders the management-headcount-planning.html template"""
    context = {
        'title': 'Headcount Planning',
        'welcome_message': 'Welcome to the headcount planning page.',
    }
    return render(request, 'apps/staffplanner/templates/management-headcount-planning.html', context)

def management_role_planning_view(request):
    """Custom role planning view that renders the management-role-planning.html template"""
    context = {
        'title': 'Role Planning',
        'welcome_message': 'Welcome to the role planning page.',
    }
    return render(request, 'apps/staffplanner/templates/management-role-planning.html', context)
