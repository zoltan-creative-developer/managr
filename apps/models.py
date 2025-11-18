from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date
from django.conf import settings

class WorkArea(models.Model):
    AREA_CHOICES = [
        ('elso_ter', 'Első tér (pepita)'),
        ('fo_vendegter', 'Fő vendégtér'),
        ('terasz', 'Terasz'),
        ('hatso_ter', 'Hátsó tér'),
        ('konyha', 'Konyha'),
        ('bar', 'Bár'),
        ('kasszak', 'Kasszák'),
        ('mosogato', 'Mosogató'),
        ('takarito', 'Takarító'),
    ]
    
    code = models.CharField(max_length=20, choices=AREA_CHOICES, default='fo_vendegter', unique=True, verbose_name="Terület kód")
    name = models.CharField(max_length=100, verbose_name="Terület neve")
    description = models.TextField(blank=True, verbose_name="Leírás")
    is_active = models.BooleanField(default=True, verbose_name="Aktív")
    
    class Meta:
        verbose_name = "Munkaterület"
        verbose_name_plural = "Munkaterületek"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class WorkRole(models.Model):
    ROLE_CHOICES = [
        ('fopincer', 'Főpincér'),
        ('pincer', 'Pincér'),
        ('pincerno', 'Pincérnő'),
        ('elso_kasszas', 'Első kasszás'),
        ('hatso_kasszas', 'Hátsó kasszás'),
        ('talalo', 'Tálaló'),
        ('teraszos', 'Teraszos'),
        ('mosogato', 'Mosogató'),
        ('takarito', 'Takarító'),
        ('eteles', 'Ételes'),
        ('elso_felvevo', 'Első felvevő'),
        ('hatso_felvevo', 'Hátsó felvevő'),
        ('kozepso_felvevo', 'Középső felvevő'),
    ]
    
    code = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True, verbose_name="Munkakör kód")
    name = models.CharField(max_length=100, verbose_name="Munkakör neve")
    description = models.TextField(blank=True, verbose_name="Leírás")
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Órabér")
    is_active = models.BooleanField(default=True, verbose_name="Aktív")
    
    class Meta:
        verbose_name = "Munkakör"
        verbose_name_plural = "Munkakörök"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class EmploymentType(models.Model):
    TYPE_CHOICES = [
        ('full_time', 'Teljes munkaidős'),
        ('part_time', 'Részmunkaidős'),
        ('temporary', 'Beugrós'),
        ('seasonal', 'Szezonális'),
        ('internship', 'Gyakornoki'),
        ('contractor', 'Vállalkozói'),
        ('volunteer', 'Önkéntes'),
    ]
    
    code = models.CharField(max_length=20, choices=TYPE_CHOICES, unique=True, verbose_name="Munkaviszony kód")
    name = models.CharField(max_length=50, verbose_name="Munkaviszony neve")
    description = models.TextField(blank=True, null=True, verbose_name="Leírás")
    
    class Meta:
        verbose_name = "Munkaviszony típus"
        verbose_name_plural = "Munkaviszony típusok"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class ShiftType(models.Model):
    """Műszak típusok"""
    SHIFT_CODES = [
        (0, 'Szabadnap'),
        (1, 'Délelőtt'),
        (10, 'Délután'),
        (11, 'Egész nap'),
    ]
    
    code = models.IntegerField(choices=SHIFT_CODES, unique=True, verbose_name="Műszak kód")
    name = models.CharField(max_length=50, verbose_name="Műszak neve")
    short_name = models.CharField(max_length=5, verbose_name="Rövidítés")
    start_time = models.TimeField(null=True, blank=True, verbose_name="Kezdési idő")
    end_time = models.TimeField(null=True, blank=True, verbose_name="Befejezési idő")
    duration_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0, verbose_name="Időtartam (óra)")
    duration_days = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name="Időtartam (nap)")
    is_paid = models.BooleanField(default=True, verbose_name="Fizetett")
    color_code = models.CharField(max_length=7, default='#FFFFFF', verbose_name="Szín kód")
    
    class Meta:
        verbose_name = "Műszak típus"
        verbose_name_plural = "Műszak típusok"
        ordering = ['code']
    
    def __str__(self):
        return f"{self.name} ({self.short_name})"

class AbsenceType(models.Model):
    TYPE_CODES = [
        ('sick_leave', 'Betegség'),
        ('vacation', 'Szabadság'),
        ('unpaid_leave', 'Fizetés nélküli szabadság'),
        ('maternity_leave', 'Gyes/Gyed'),
        ('meeting', 'Munkatársi megbeszélés'),
        ('lecture', 'Előadás/közösségi nap'),
        ('training', 'Képzés'),
        ('other', 'Egyéb'),
    ]
    
    code = models.CharField(max_length=20, choices=TYPE_CODES, unique=True, verbose_name="Hiányzás kód")
    name = models.CharField(max_length=50, verbose_name="Hiányzás neve")
    description = models.TextField(blank=True, null=True, verbose_name="Leírás")
    
    class Meta:
        verbose_name = "Hiányzás típus"
        verbose_name_plural = "Hiányzás típusok"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Kérem adjon meg egy érvényes email címet!")
        if not password:
            raise ValueError("Kérem adjon meg egy érvényes jelszót!")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)

    is_active = models.BooleanField(default=True, verbose_name="Aktív")
    is_staff = models.BooleanField(default=False, verbose_name="Személyzet")
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['last_name', 'first_name', 'password']

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Felhasználó"
        verbose_name_plural = "Felhasználók"

    def __str__(self):
        return f"{self.email}"

    def get_full_name(self):
        return f"{self.last_name} {self.first_name}".strip()
    
    def get_short_name(self):
        return self.first_name
    
    def deactivate(self):
        self.is_active = False
        self.save()

class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Felhasználó")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Születési dátum")
    gender = models.CharField(blank=True, null=True, max_length=1, verbose_name="Nem") # F vagy N
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefonszám")
    address = models.TextField(blank=True, null=True, verbose_name="Cím")

    # Munkaviszony adatok
    hire_date = models.DateField(null=True, blank=True, default=date.today(), verbose_name="Belépés dátuma")
    employment_type = models.ForeignKey(EmploymentType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Munkaviszony típusa")
    absence_type = models.ForeignKey(AbsenceType, on_delete=models.SET_NULL, null=True, blank=True, default=None, verbose_name="Hiányzás típusa")
    default_work_role = models.ForeignKey(WorkRole, on_delete=models.SET_NULL, null=True, blank=True, default=None, verbose_name="Alapértelmezett munkakör")
    min_full_shifts_per_month = models.IntegerField(null=True, blank=True, default=10, verbose_name="Min havi teljes műszakok összesen")
    max_hours_per_day = models.IntegerField(null=True, blank=True, default=12, verbose_name="Max napi óraszám")
    max_full_shifts_per_week = models.IntegerField(null=True, blank=True, default=5, verbose_name="Max heti teljes műszakok összesen")

    class Meta:
        verbose_name = "Dolgozó"
        verbose_name_plural = "Dolgozók"
        ordering = ['user__first_name', 'user__last_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.pk})"
    
    def full_name(self):
        return self.user.get_full_name()

class EmployeeRequests(models.Model):
    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Dolgozó")
    year = models.IntegerField(verbose_name="Év")
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], verbose_name="Hónap")
    request_data = models.JSONField(verbose_name="Igény adatok")

class StaffSchedules(models.Model):
    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Dolgozó")
    year = models.IntegerField(verbose_name="Év")
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], verbose_name="Hónap")
    schedule_data = models.JSONField(verbose_name="Beosztás adatok")
    
    class Meta:
        verbose_name = "Dolgozói beosztás összefoglaló"
        verbose_name_plural = "Dolgozói beosztás összefoglalók"
        unique_together = ['employee', 'year', 'month']
    
    def __str__(self):
        return f"{self.employee.display_name}, {self.year}, {self.month}: {self.schedule_data}"