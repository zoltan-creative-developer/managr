from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

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
    last_name = models.CharField(max_length=150, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_login = models.DateTimeField(blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('vezeto', 'Vezető'),
        ('dolgozo', 'Dolgozó'),
        ('pincer', 'Pincér'),
        ('pincerno', 'Pincérnő'),
        ('elso_kasszas', 'Első kasszás'),
        ('hatso_kasszas', 'Hátsó kasszás'),
        ('talalo', 'Tálaló'),
        ('terasz_pincer', 'Terasz pincér'),
        ('terasz_pincerno', 'terasz pincérnő'),
        ('eteles', 'Ételes'),
        ('elso_felvevo', 'Első felvevő'),
        ('hatso_felvevo', 'Hátsó felvevő'),
        ('kozepso_felvevo', 'Középső felvevő'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='dolgozo', verbose_name="Szerepkör")

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

class WorkArea(models.Model):
    """Munkaterületek (pl. első tér, terasz, hátsó tér)"""
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
    
    code = models.CharField(max_length=20, choices=AREA_CHOICES, unique=True, verbose_name="Terület kód")
    name = models.CharField(max_length=100, verbose_name="Terület neve")
    description = models.TextField(blank=True, verbose_name="Leírás")
    is_active = models.BooleanField(default=True, verbose_name="Aktív")
    priority = models.IntegerField(default=1, verbose_name="Prioritás")
    
    class Meta:
        verbose_name = "Munkaterület"
        verbose_name_plural = "Munkaterületek"
        ordering = ['priority', 'name']
    
    def __str__(self):
        return self.name

class WorkRole(models.Model):
    """Munkakörök (pincér, kasszás, stb.)"""
    ROLE_CHOICES = [
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
    work_areas = models.ManyToManyField(WorkArea, verbose_name="Munkaterületek")
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Órabér")
    is_active = models.BooleanField(default=True, verbose_name="Aktív")
    
    class Meta:
        verbose_name = "Munkakör"
        verbose_name_plural = "Munkakörök"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    """Dolgozók (kiterjesztett információkkal)"""
    GENDER_CHOICES = [
        ('F', 'Nő'),
        ('M', 'Férfi'),
        ('O', 'Egyéb'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name="Felhasználó")
    employee_id = models.CharField(max_length=10, unique=True, verbose_name="Dolgozó azonosító")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Születési dátum")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name="Nem")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Telefonszám")
    address = models.TextField(blank=True, verbose_name="Cím")
    
    # Munkaviszony adatok
    hire_date = models.DateField(verbose_name="Belépés dátuma")
    work_roles = models.ManyToManyField(WorkRole, verbose_name="Munkakörök")
    primary_work_area = models.ForeignKey(WorkArea, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Elsődleges munkaterület")
    is_full_time = models.BooleanField(default=True, verbose_name="Teljes munkaidős")
    max_hours_per_week = models.IntegerField(default=40, verbose_name="Max heti óraszám")
    max_days_per_week = models.IntegerField(default=6, verbose_name="Max heti napok")
    
    # Személyes adatok kezelése
    emergency_contact_name = models.CharField(max_length=100, blank=True, verbose_name="Segélyhívó neve")
    emergency_contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Segélyhívó telefonja")
    
    # Excel kompatibilitás
    excel_code = models.CharField(max_length=10, blank=True, verbose_name="Excel kód (pl. BGJ)")
    notes = models.TextField(blank=True, verbose_name="Megjegyzések")
    
    is_active = models.BooleanField(default=True, verbose_name="Aktív")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dolgozó"
        verbose_name_plural = "Dolgozók"
        ordering = ['user__last_name', 'user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def display_name(self):
        return self.excel_code if self.excel_code else self.full_name
    
    def get_primary_role(self):
        return self.work_roles.first()

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

class MonthlySchedule(models.Model):
    """Havi beosztások"""
    year = models.IntegerField(verbose_name="Év")
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], verbose_name="Hónap")
    name = models.CharField(max_length=100, verbose_name="Beosztás neve")
    description = models.TextField(blank=True, verbose_name="Leírás")
    
    # Metaadatok
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, verbose_name="Létrehozta")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Létrehozás dátuma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Módosítás dátuma")
    
    # Státusz kezelés
    STATUS_CHOICES = [
        ('draft', 'Tervezet'),
        ('in_review', 'Felülvizsgálat alatt'),
        ('approved', 'Jóváhagyott'),
        ('published', 'Közzétett'),
        ('archived', 'Archivált'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Státusz")
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_schedules', verbose_name="Jóváhagyta")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Jóváhagyás dátuma")
    
    # Számított mezők
    total_assignments = models.IntegerField(default=0, verbose_name="Összes beosztás")
    total_work_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Összes munkaóra")
    
    class Meta:
        verbose_name = "Havi beosztás"
        verbose_name_plural = "Havi beosztások"
        unique_together = ['year', 'month', 'name']
        ordering = ['-year', '-month', 'name']
    
    def __str__(self):
        return f"{self.year}/{self.month:02d} - {self.name}"
    
    @property
    def month_name(self):
        month_names = {
            1: 'Január', 2: 'Február', 3: 'Március', 4: 'Április',
            5: 'Május', 6: 'Június', 7: 'Július', 8: 'Augusztus',
            9: 'Szeptember', 10: 'Október', 11: 'November', 12: 'December'
        }
        return month_names.get(self.month, str(self.month))
    
    def get_days_in_month(self):
        """Visszaadja a hónap napjainak számát"""
        import calendar
        return calendar.monthrange(self.year, self.month)[1]

    def get_weekend_days(self):
        """Visszaadja a hónap azon napjait (1-indexelve), amelyek szombatra vagy vasárnapra esnek."""
        weekend_days = set()
        for day in range(1, self.get_days_in_month() + 1):
            weekday = date(self.year, self.month, day).weekday()  # 5=Saturday, 6=Sunday
            if weekday in (5, 6):
                weekend_days.add(day)
        return weekend_days

class ScheduleAssignment(models.Model):
    """Beosztás hozzárendelések (egy dolgozó egy napra)"""
    schedule = models.ForeignKey(MonthlySchedule, on_delete=models.CASCADE, verbose_name="Havi beosztás")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Dolgozó")
    day = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(31)], verbose_name="Nap")
    shift_type = models.ForeignKey(ShiftType, on_delete=models.CASCADE, verbose_name="Műszak típus")
    work_area = models.ForeignKey(WorkArea, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Munkaterület")
    
    # Kiegészítő információk
    notes = models.TextField(blank=True, verbose_name="Megjegyzések")
    is_overtime = models.BooleanField(default=False, verbose_name="Túlóra")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Beosztás hozzárendelés"
        verbose_name_plural = "Beosztás hozzárendelések"
        unique_together = ['schedule', 'employee', 'day']
        ordering = ['schedule', 'day', 'employee']
    
    def __str__(self):
        return f"{self.schedule} - {self.employee.display_name} - {self.day}. nap: {self.shift_type.short_name}"

class EmployeeRequests(models.Model):
    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Dolgozó")
    year = models.IntegerField(verbose_name="Év")
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], verbose_name="Hónap")
    request_data = models.JSONField(verbose_name="Igény adatok")
    
class DayCell(models.Model):
    """
    Opcionális: menti az adott nap színét.
    date: ISO string 'YYYY-MM-DD' vagy DateField használható.
    color: 'green' vagy 'red'
    """
    date = models.DateField(unique=True)
    color = models.CharField(max_length=5, choices=(('green', 'Zöld'), ('red', 'Piros')), default='green')

    def __str__(self):
        return f"{self.date} -> {self.color}"

class EmployeePreference(models.Model):
    """Dolgozói preferenciák Excel integrációval"""
    PREFERENCE_TYPES = [
        ('availability', 'Elérhetőség'),
        ('unavailability', 'Nem elérhető'),
        ('preferred_shift', 'Preferált műszak'),
        ('preferred_area', 'Preferált munkaterület'),
        ('max_consecutive_days', 'Max egymás utáni napok'),
        ('min_rest_days', 'Min pihenőnapok'),
        ('special_request', 'Speciális kérés'),
        ('recurring_pattern', 'Ismétlődő minta'),
        ('excel_note', 'Excel megjegyzés'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Alacsony'),
        ('medium', 'Közepes'),
        ('high', 'Magas'),
        ('critical', 'Kritikus'),
    ]
    
    COLOR_CODES = [
        ('green', 'Zöld - Rugalmas'),
        ('blue', 'Kék - Várható'),
        ('orange', 'Narancs - Fix de mozgatható'),
        ('red', 'Piros - Mozgatthatatlan'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Dolgozó")
    schedule = models.ForeignKey(MonthlySchedule, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Havi beosztás")
    
    # Preferencia adatok
    preference_type = models.CharField(max_length=30, choices=PREFERENCE_TYPES, default='availability', verbose_name="Preferencia típus")
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium', verbose_name="Prioritás")
    color_code = models.CharField(max_length=10, choices=COLOR_CODES, default='green', verbose_name="Szín kód")
    
    # Időbeli meghatározás
    specific_date = models.DateField(null=True, blank=True, verbose_name="Konkrét dátum")
    day_of_month = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(31)], verbose_name="Hónap napja")
    day_of_week = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(6)], verbose_name="Hét napja")
    start_date = models.DateField(null=True, blank=True, verbose_name="Kezdő dátum")
    end_date = models.DateField(null=True, blank=True, verbose_name="Befejező dátum")
    
    # Preferencia részletei
    preferred_shift_type = models.ForeignKey(ShiftType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Preferált műszak")
    preferred_work_area = models.ForeignKey(WorkArea, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Preferált munkaterület")
    
    # Excel kompatibilitás
    excel_original_text = models.TextField(blank=True, verbose_name="Eredeti Excel szöveg")
    parsed_data = models.JSONField(blank=True, null=True, verbose_name="Feldolgozott adatok")
    
    # Megjegyzések és részletek
    description = models.TextField(blank=True, verbose_name="Leírás")
    notes = models.TextField(blank=True, verbose_name="Megjegyzések")
    
    # Kezelés
    is_active = models.BooleanField(default=True, verbose_name="Aktív")
    is_recurring = models.BooleanField(default=False, verbose_name="Ismétlődő")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dolgozói preferencia"
        verbose_name_plural = "Dolgozói preferenciák"
        ordering = ['-priority', 'employee', 'specific_date']
    
    def __str__(self):
        date_info = self.specific_date.strftime("%Y-%m-%d") if self.specific_date else "Általános"
        return f"{self.employee.display_name} - {self.get_preference_type_display()} ({date_info})"

class ScheduleStatistics(models.Model):
    """Beosztás statisztikák"""
    schedule = models.OneToOneField(MonthlySchedule, on_delete=models.CASCADE, verbose_name="Havi beosztás")
    
    # Alapvető számok
    total_employees = models.IntegerField(default=0, verbose_name="Összes dolgozó")
    total_work_days = models.IntegerField(default=0, verbose_name="Összes munkanap")
    total_work_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Összes munkaóra")
    
    # Műszak szerinti bontás
    morning_shifts = models.IntegerField(default=0, verbose_name="Délelőtti műszakok")
    afternoon_shifts = models.IntegerField(default=0, verbose_name="Délutáni műszakok")
    full_day_shifts = models.IntegerField(default=0, verbose_name="Egész napos műszakok")
    free_days = models.IntegerField(default=0, verbose_name="Szabadnapok")
    
    # Átlagok
    avg_hours_per_employee = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="Átlag óra/dolgozó")
    avg_days_per_employee = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="Átlag nap/dolgozó")
    
    # Költségek
    estimated_total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Becsült összes költség")
    
    # Metaadatok
    calculated_at = models.DateTimeField(auto_now=True, verbose_name="Számítás dátuma")
    
    class Meta:
        verbose_name = "Beosztás statisztika"
        verbose_name_plural = "Beosztás statisztikák"
    
    def __str__(self):
        return f"Statisztika: {self.schedule}"
