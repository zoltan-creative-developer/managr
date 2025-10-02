from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from apps.models import CustomUser

class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'password1', 'password2', 'last_name', 'first_name', 'is_active', 'is_staff', 'is_superuser']

class EditForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'last_name', 'first_name', 'is_active', 'is_staff', 'is_superuser']

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    add_form = RegisterForm
    form = EditForm
    
    list_display = (
    'id',
    'email',
    'last_name',
    'first_name',
    'is_active',
    'is_staff',
    'is_superuser',
    'last_login',
    'date_joined',
    )

    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',
        'last_login',
    )

    search_fields = (
        'email',
        'last_name',
        'first_name',
    )

    fieldsets = (
        ('Fiókazonosító adatok', {
            'fields': ('email', 'password')
        }),
        ('Név', {
            'fields': ('last_name', 'first_name')
        }),
        ('Jogosultságok', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        ('Aktivitás', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'last_name', 'first_name')}
        ),
    )
    ordering = ('last_name', 'first_name', 'email')

# Register CustomUser with custom admin
admin.site.unregister(CustomUser) if admin.site.is_registered(CustomUser) else None
admin.site.register(CustomUser, CustomUserAdmin)


    ###

# class EmployeeInline(admin.StackedInline):
#     model = Employee
#     can_delete = False

# class CustomUserAdmin(UserAdmin):
#     inlines = [EmployeeInline]


# class MyModelAdmin(admin.ModelAdmin):
#     class Media:
#         css = {
#             'all': ('css/custom_admin.css',)
#         }

# fieldset.wide .form-row {
#     width: 100%;
#     background-color: #f9f9f9; /* Optional: visual cue */
# }
# https://dnmtechs.com/overriding-css-in-django-admin-python-3-programming/