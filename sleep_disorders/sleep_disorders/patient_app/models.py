from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from django.core.validators import RegexValidator
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.conf import settings

'''
class Company(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Official company name"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-friendly identifier for the company",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Brief company overview"
    )

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.slug})"


class CustomUser(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be in format: '+999999999'. Up to 15 digits allowed."
    )

    profile_image = models.ImageField(
    upload_to='profile_images/',
    null=True,
    blank=True,
    verbose_name="Profile Image",
    help_text="Upload a profile picture",
    validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
)
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name="Associated Company",
        help_text="Company the user belongs to",
        null=True,
        blank=True,
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Contact Number",
        help_text="User's primary contact number"
    )
    job_title = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Job Title",
        help_text="User's official position in the company"
    )
    is_company_admin = models.BooleanField(
        default=False,
        verbose_name="Company Administrator",
        help_text="Designates whether the user can manage company-level settings"
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=['company', 'is_active']),
        ]

    def __str__(self):
        return f"{self.username})"

    def clean(self):
        """Add custom validation logic"""
        super().clean()
        if self.phone_number:
            self.phone_number = self.phone_number.strip()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
'''


class Patient(models.Model):
    """Main patient model to link all forms"""
    # Basic Information
    patient_id = models.CharField(max_length=20, unique=True, verbose_name="شناسه بیمار")
    first_name = models.CharField(max_length=100, verbose_name="نام")
    last_name = models.CharField(max_length=100, verbose_name="نام خانوادگی")
    national_id = models.CharField(max_length=10, unique=True, verbose_name="کد ملی", blank=True, null=True)
    
    # Contact Information
    phone = models.CharField(max_length=15, verbose_name="تلفن همراه")
    email = models.EmailField(blank=True, null=True, verbose_name="پست الکترونیکی")
    emergency_contact_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="نام فرد تماس اضطراری")
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="تلفن تماس اضطراری")
    
    # Demographics
    GENDER_CHOICES = [
        ('M', 'مرد'),
        ('F', 'زن'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="جنسیت")
    birth_date = models.DateField(verbose_name="تاریخ تولد")
    
    # Physical Measurements
    height = models.IntegerField(validators=[MinValueValidator(50), MaxValueValidator(250)], 
                                 verbose_name="قد (سانتی متر)")
    weight = models.DecimalField(max_digits=5, decimal_places=2, 
                                validators=[MinValueValidator(20), MaxValueValidator(300)],
                                verbose_name="وزن (کیلوگرم)")
    neck_circumference = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True,
                                           verbose_name="اندازه دور گردن")
    bmi = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True,
                             verbose_name="BMI")
    
    # Administrative
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ آخرین ویرایش")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                  related_name='created_patients', verbose_name="ایجاد کننده")
    
    class Meta:
        verbose_name = "بیمار"
        verbose_name_plural = "بیماران"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.patient_id}"
    
    def calculate_bmi(self):
        """Calculate BMI from height and weight"""
        if self.height and self.weight:
            height_m = self.height / 100
            self.bmi = round(float(self.weight) / (height_m ** 2), 2)
            return self.bmi
        return None
    
    def save(self, *args, **kwargs):
        self.calculate_bmi()
        super().save(*args, **kwargs)


# Form 1: Patient Information and Initial Assessment
class PatientInformation(models.Model):
    """Form 1 - Initial patient information and symptoms"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='information_forms')
    form_date = models.DateField(default=timezone.now, verbose_name="تاریخ فرم")
    
    # Symptoms Checklist
    snoring = models.BooleanField(default=False, verbose_name="خرخر")
    witnessed_apnea = models.BooleanField(default=False, verbose_name="آپنه مشاهده شده")
    morning_confusion = models.BooleanField(default=False, verbose_name="گیجی صبح")
    morning_dry_mouth = models.BooleanField(default=False, verbose_name="خشکی دهان صبح")
    morning_nausea = models.BooleanField(default=False, verbose_name="تهوع صبح")
    excessive_daytime_sleepiness = models.BooleanField(default=False, verbose_name="خواب آلودگی مفرط روزانه")
    depression = models.BooleanField(default=False, verbose_name="افسردگی")
    decreased_libido = models.BooleanField(default=False, verbose_name="کاهش میل جنسی")
    
    # Previous Sleep Studies
    previous_sleep_test = models.BooleanField(default=False, verbose_name="آیا بیمار قبلا تست خواب انجام داده است؟")
    previous_apnea_diagnosis = models.BooleanField(default=False, verbose_name="آیا بیمار قبلا تشخیص وقفه تنفسی داشته است؟")
    previous_pap_therapy = models.BooleanField(default=False, verbose_name="آیا بیمار از فشار درمانی راههای هوایی استفاده کرده است؟")
    previous_surgery = models.BooleanField(default=False, verbose_name="آیا بیمار قبلا برای وقفه تنفسی جراحی داشته است؟")
    oxygen_supplement = models.BooleanField(default=False, verbose_name="آیا بیمار از مکمل اکسیژن استفاده می کند؟")
    
    # Additional Comments
    comments = models.TextField(blank=True, null=True, verbose_name="توضیحات اضافی")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "فرم اطلاعات بیمار"
        verbose_name_plural = "فرم های اطلاعات بیمار"
        ordering = ['-form_date']
    
    def __str__(self):
        return f"اطلاعات بیمار - {self.patient} - {self.form_date}"


# Form 2: Epworth Sleepiness Scale
class EpworthSleepinessScale(models.Model):
    """Form 2 - Epworth Sleepiness Scale assessment"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='epworth_forms')
    form_date = models.DateField(default=timezone.now, verbose_name="تاریخ فرم")
    
    # ESS Questions (0-3 scale)
    SCORE_CHOICES = [
        (0, 'هرگز چرت نمی زنم'),
        (1, 'احتمال کم چرت می زنم'),
        (2, 'احتمال متوسط چرت می زنم'),
        (3, 'احتمال زیاد چرت می زنم'),
    ]
    
    sitting_reading = models.IntegerField(choices=SCORE_CHOICES, verbose_name="نشستن و مطالعه کردن")
    watching_tv = models.IntegerField(choices=SCORE_CHOICES, verbose_name="تماشای تلویزیون")
    sitting_inactive = models.IntegerField(choices=SCORE_CHOICES, 
                                         verbose_name="نشستن غیر فعال در یک مکان عمومی")
    car_passenger = models.IntegerField(choices=SCORE_CHOICES, 
                                      verbose_name="نشستن در یک اتومبیل به عنوان مسافر")
    lying_down = models.IntegerField(choices=SCORE_CHOICES, 
                                    verbose_name="دراز کشیدن برای استراحت در بعدازظهر")
    sitting_talking = models.IntegerField(choices=SCORE_CHOICES, verbose_name="نشستن و با کسی صحبت کردن")
    after_lunch = models.IntegerField(choices=SCORE_CHOICES, verbose_name="آرام نشستن بعد از نهار")
    in_traffic = models.IntegerField(choices=SCORE_CHOICES, 
                                   verbose_name="توقف در ترافیک")
    
    # Additional Questions
    loud_snoring = models.BooleanField(verbose_name="با صدای بلند خروپف می کنید؟")
    wake_breathless = models.BooleanField(verbose_name="در حالیکه نفس شما می رود از خواب بیدار می شوم")
    wake_tired = models.BooleanField(verbose_name="صبح ها خسته از خواب بیدار می شوم")
    sleep_difficulty = models.BooleanField(verbose_name="برای اینکه خواب برد مشکل دارم")
    restful_sleep = models.BooleanField(verbose_name="خواب بسیار آرامی دارم")
    unusual_behaviors = models.BooleanField(verbose_name="خواب در اثر اختلالات غیر معمول")
    nightmares = models.BooleanField(verbose_name="رویاهای شبانه، کابوس")
    sleep_driving = models.BooleanField(verbose_name="در حال رانندگی خواب می برد")
    other_symptoms = models.TextField(blank=True, null=True, 
                                    verbose_name="سایر علائم گزارش شده")
    
    # Calculated total score
    total_score = models.IntegerField(blank=True, null=True, verbose_name="نمره کل")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "مقیاس خواب آلودگی اپورث"
        verbose_name_plural = "مقیاس های خواب آلودگی اپورث"
        ordering = ['-form_date']
    
    def calculate_total_score(self):
        """Calculate total Epworth score"""
        fields = ['sitting_reading', 'watching_tv', 'sitting_inactive', 'car_passenger',
                  'lying_down', 'sitting_talking', 'after_lunch', 'in_traffic']
        total = sum(getattr(self, field) for field in fields if getattr(self, field) is not None)
        self.total_score = total
        return total
    
    def save(self, *args, **kwargs):
        self.calculate_total_score()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"ESS - {self.patient} - Score: {self.total_score} - {self.form_date}"


# Form 3: Medical History
class MedicalHistory(models.Model):
    """Form 3 - Patient medical history and conditions"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_history_forms')
    form_date = models.DateField(default=timezone.now, verbose_name="تاریخ فرم")
    
    # Sleep Schedule Questions
    sleep_thoughts = models.TextField(blank=True, null=True, 
                                    verbose_name="هنگام خوابیدن چقدر می گذرد تا که فکر شده ام")
    wake_time = models.TextField(blank=True, null=True, 
                               verbose_name="بعد از یک روز، چقدر زمان می گیرد")
    morning_routine = models.TextField(blank=True, null=True, 
                                     verbose_name="وقتی صبح از خواب بیدار می شوم")
    wake_activities = models.TextField(blank=True, null=True, 
                                     verbose_name="آنچه می دانیم بیدار هستیم")
    drowsy_activities = models.TextField(blank=True, null=True, 
                                       verbose_name="درست بعد یا قبل از چرت زدن")
    sleep_paralysis = models.TextField(blank=True, null=True, 
                                     verbose_name="وقتی خواب از صبح بیدار می شوم حس قلع بودن")
    cataplexy = models.TextField(blank=True, null=True, 
                               verbose_name="وقتی می خندم زانوانم سست می شوند")
    
    # Medical Conditions - Current and Past
    diabetes_current = models.BooleanField(default=False, verbose_name="دیابت - فعلی")
    diabetes_past = models.BooleanField(default=False, verbose_name="دیابت - گذشته")
    hypertension_current = models.BooleanField(default=False, verbose_name="فشار خون بالا - فعلی")
    hypertension_past = models.BooleanField(default=False, verbose_name="فشار خون بالا - گذشته")
    stroke_current = models.BooleanField(default=False, verbose_name="سکته مغزی - فعلی")
    stroke_past = models.BooleanField(default=False, verbose_name="سکته مغزی - گذشته")
    heart_problems_current = models.BooleanField(default=False, verbose_name="مشکلات قلبی - فعلی")
    heart_problems_past = models.BooleanField(default=False, verbose_name="مشکلات قلبی - گذشته")
    heart_attack_current = models.BooleanField(default=False, verbose_name="حملات قلبی - فعلی")
    heart_attack_past = models.BooleanField(default=False, verbose_name="حملات قلبی - گذشته")
    angina_current = models.BooleanField(default=False, verbose_name="آنژین - فعلی")
    angina_past = models.BooleanField(default=False, verbose_name="آنژین - گذشته")
    arrhythmia_current = models.BooleanField(default=False, verbose_name="آریتمی - فعلی")
    arrhythmia_past = models.BooleanField(default=False, verbose_name="آریتمی - گذشته")
    asthma_current = models.BooleanField(default=False, verbose_name="آسم - فعلی")
    asthma_past = models.BooleanField(default=False, verbose_name="آسم - گذشته")
    tuberculosis_current = models.BooleanField(default=False, verbose_name="سل - فعلی")
    tuberculosis_past = models.BooleanField(default=False, verbose_name="سل - گذشته")
    lung_disease_current = models.BooleanField(default=False, verbose_name="بیماری ریوی - فعلی")
    lung_disease_past = models.BooleanField(default=False, verbose_name="بیماری ریوی - گذشته")
    nasal_congestion_current = models.BooleanField(default=False, verbose_name="گرفتگی بینی - فعلی")
    nasal_congestion_past = models.BooleanField(default=False, verbose_name="گرفتگی بینی - گذشته")
    jaw_problems_current = models.BooleanField(default=False, verbose_name="مشکلات فک - فعلی")
    jaw_problems_past = models.BooleanField(default=False, verbose_name="مشکلات فک - گذشته")
    neurological_current = models.BooleanField(default=False, verbose_name="مشکلات عصبی - فعلی")
    neurological_past = models.BooleanField(default=False, verbose_name="مشکلات عصبی - گذشته")
    prostate_current = models.BooleanField(default=False, verbose_name="پروستات - فعلی")
    prostate_past = models.BooleanField(default=False, verbose_name="پروستات - گذشته")
    alcohol_problem_current = models.BooleanField(default=False, verbose_name="مشکل الکل - فعلی")
    alcohol_problem_past = models.BooleanField(default=False, verbose_name="مشکل الکل - گذشته")
    addiction_current = models.BooleanField(default=False, verbose_name="اعتیاد - فعلی")
    addiction_past = models.BooleanField(default=False, verbose_name="اعتیاد - گذشته")
    depression_current = models.BooleanField(default=False, verbose_name="افسردگی - فعلی")
    depression_past = models.BooleanField(default=False, verbose_name="افسردگی - گذشته")
    fainting_current = models.BooleanField(default=False, verbose_name="حملات از حال رفتن - فعلی")
    fainting_past = models.BooleanField(default=False, verbose_name="حملات از حال رفتن - گذشته")
    
    # Sleep Quality Rating
    QUALITY_CHOICES = [
        ('very_bad', 'خیلی بد'),
        ('bad', 'بد'),
        ('average', 'متوسط'),
        ('good', 'خوب'),
        ('excellent', 'عالی'),
    ]
    sleep_quality = models.CharField(max_length=20, choices=QUALITY_CHOICES, blank=True, null=True,
                                   verbose_name="کیفیت خواب")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "سابقه پزشکی"
        verbose_name_plural = "سوابق پزشکی"
        ordering = ['-form_date']
    
    def __str__(self):
        return f"سابقه پزشکی - {self.patient} - {self.form_date}"


# Form 4: Physical Examination
class PhysicalExamination(models.Model):
    """Form 4 - Physical examination and measurements"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='physical_exams')
    form_date = models.DateField(default=timezone.now, verbose_name="تاریخ فرم")
    physician = models.CharField(max_length=200, blank=True, null=True, verbose_name="پزشک معرف")
    
    # Study Types
    baseline_diagnostic = models.BooleanField(default=False, verbose_name="Baseline Diagnostic Study")
    full_night_titration = models.BooleanField(default=False, verbose_name="Full Night Titration Study")
    split_night = models.BooleanField(default=False, verbose_name="Split Night Study")
    re_titration = models.BooleanField(default=False, verbose_name="Re-Titration Study")
    home_sleep_testing = models.BooleanField(default=False, verbose_name="Home Sleep Testing Study")
    
    # Interpreting Physician
    PHYSICIAN_CHOICES = [
        ('sharafkhaneh', 'Prof. Sharafkhaneh'),
        ('ansarin', 'Prof. Ansarin'),
        ('other', 'Other'),
    ]
    interpreting_physician = models.CharField(max_length=20, choices=PHYSICIAN_CHOICES, 
                                            verbose_name="Interpreting physician")
    other_physician = models.CharField(max_length=200, blank=True, null=True, 
                                     verbose_name="Other physician name")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "معاینات بالینی"
        verbose_name_plural = "معاینات بالینی"
        ordering = ['-form_date']
    
    def __str__(self):
        return f"معاینه بالینی - {self.patient} - {self.form_date}"


# Form 5: Daily Symptom Assessment
class DailySymptomAssessment(models.Model):
    """Form 5 - Daily symptom tracking"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='symptom_assessments')
    form_date = models.DateField(default=timezone.now, verbose_name="تاریخ فرم")
    
    # Nap Information
    morning_naps_count = models.IntegerField(default=0, verbose_name="تعداد چرت صبح")
    morning_naps_duration = models.IntegerField(default=0, verbose_name="مدت چرت صبح (دقیقه)")
    night_naps_count = models.IntegerField(default=0, verbose_name="تعداد چرت شب")
    night_naps_duration = models.IntegerField(default=0, verbose_name="مدت چرت شب (دقیقه)")
    recent_naps_count = models.IntegerField(default=0, verbose_name="تعداد چرت های اخیر")
    recent_naps_duration = models.IntegerField(default=0, verbose_name="مدت چرت های اخیر (دقیقه)")
    
    # Substance Use
    caffeine_count_today = models.IntegerField(default=0, verbose_name="مصرف کافئین امروز")
    caffeine_count_recent = models.IntegerField(default=0, verbose_name="مصرف کافئین اخیر")
    alcohol_count_today = models.IntegerField(default=0, verbose_name="مصرف الکل امروز")
    alcohol_count_recent = models.IntegerField(default=0, verbose_name="مصرف الکل اخیر")
    
    # Symptom Comparisons
    COMPARISON_CHOICES = [
        ('less', 'کم'),
        ('same', 'به همان اندازه'),
        ('more', 'بیشتر'),
        ('no', 'خیر'),
    ]
    
    sleepiness_today = models.CharField(max_length=10, choices=COMPARISON_CHOICES, 
                                      verbose_name="خواب آلودگی امروز")
    tiredness_today = models.CharField(max_length=10, choices=COMPARISON_CHOICES, 
                                     verbose_name="خستگی امروز")
    physical_activity = models.CharField(max_length=10, choices=COMPARISON_CHOICES, 
                                       verbose_name="فعالیت فیزیکی")
    feeling_sick = models.CharField(max_length=10, choices=COMPARISON_CHOICES, 
                                  verbose_name="احساس بیماری")
    anxiety_today = models.CharField(max_length=10, choices=COMPARISON_CHOICES, 
                                   verbose_name="اضطراب امروز")
    depression_today = models.CharField(max_length=10, choices=COMPARISON_CHOICES, 
                                      verbose_name="افسردگی امروز")
    sleepy_now = models.CharField(max_length=10, choices=COMPARISON_CHOICES, 
                                verbose_name="خواب آلودگی فعلی")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "ارزیابی علائم روزانه"
        verbose_name_plural = "ارزیابی های علائم روزانه"
        ordering = ['-form_date']
    
    def __str__(self):
        return f"علائم روزانه - {self.patient} - {self.form_date}"


# Form 6: Clinical Examination Details
class ClinicalExaminationDetails(models.Model):
    """Form 6 - Detailed clinical examination"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='clinical_details')
    form_date = models.DateField(default=timezone.now, verbose_name="تاریخ فرم")
    
    # Sleep Schedule
    weekday_bedtime = models.TimeField(blank=True, null=True, verbose_name="ساعت خواب روزهای هفته")
    weekday_waketime = models.TimeField(blank=True, null=True, verbose_name="ساعت بیداری روزهای هفته")
    weekend_bedtime = models.TimeField(blank=True, null=True, verbose_name="ساعت خواب آخر هفته")
    weekend_waketime = models.TimeField(blank=True, null=True, verbose_name="ساعت بیداری آخر هفته")
    
    # Work Schedule
    shift_work = models.BooleanField(default=False, verbose_name="کار شیفتی")
    shift_work_description = models.TextField(blank=True, null=True, verbose_name="توضیحات کار شیفتی")
    
    # Throat Examination
    small_mouth_throat = models.BooleanField(default=False, verbose_name="دهان کوچک و گلوی باریک")
    small_mouth_soft_palate = models.BooleanField(default=False, verbose_name="دهان کوچک با کام نرم")
    normal_mouth_soft_palate = models.BooleanField(default=False, verbose_name="دهان طبیعی با کام نرم")
    normal_mouth_visible_uvula = models.BooleanField(default=False, verbose_name="دهان طبیعی با زبان کوچک")
    normal_mouth_visible_tonsils = models.BooleanField(default=False, verbose_name="دهان طبیعی با لوزه")
    mouth_with_large_tonsils = models.BooleanField(default=False, verbose_name="دهان با لوزه های بزرگ")
    large_tongue = models.BooleanField(default=False, verbose_name="زبان بزرگ")
    
    # Nasal Examination
    nasal_congestion_right = models.BooleanField(default=False, verbose_name="گرفتگی بینی راست")
    nasal_congestion_left = models.BooleanField(default=False, verbose_name="گرفتگی بینی چپ")
    nasal_deviation = models.BooleanField(default=False, verbose_name="انحراف بینی")
    
    # Additional Symptoms
    loud_snoring = models.BooleanField(default=False, verbose_name="خروپف بلند")
    choking_episodes = models.BooleanField(default=False, verbose_name="احساس خفگی")
    witnessed_apnea = models.BooleanField(default=False, verbose_name="آپنه مشاهده شده")
    restless_sleep = models.BooleanField(default=False, verbose_name="خواب ناآرام")
    sleep_walking = models.BooleanField(default=False, verbose_name="راه رفتن در خواب")
    night_terrors = models.BooleanField(default=False, verbose_name="وحشت شبانه")
    morning_headaches = models.BooleanField(default=False, verbose_name="سردرد صبحگاهی")
    dry_mouth = models.BooleanField(default=False, verbose_name="خشکی دهان")
    nightmares = models.BooleanField(default=False, verbose_name="کابوس")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "جزئیات معاینه بالینی"
        verbose_name_plural = "جزئیات معاینات بالینی"
        ordering = ['-form_date']
    
    def __str__(self):
        return f"جزئیات بالینی - {self.patient} - {self.form_date}"


# Form 7: PAP Titration
class PAPTitration(models.Model):
    """Form 7 - PAP titration results and feedback"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='pap_titrations')
    form_date = models.DateField(default=timezone.now, verbose_name="تاریخ فرم")
    
    # Morning Feeling
    FEELING_CHOICES = [
        ('much_better', 'خیلی بهتر'),
        ('better', 'بهتر'),
        ('same', 'یکسان'),
        ('worse', 'بدتر'),
        ('much_worse', 'خیلی بدتر'),
    ]
    morning_feeling = models.CharField(max_length=20, choices=FEELING_CHOICES, 
                                     verbose_name="احساس صبح")
    
    # PAP Experience
    EXPERIENCE_CHOICES = [
        ('none', 'اصلا'),
        ('little', 'کم'),
        ('moderate', 'تا حدودی'),
        ('good', 'خوب'),
        ('excellent', 'خیلی'),
    ]
    pap_improvement = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, 
                                     verbose_name="بهبود با PAP")
    mask_ease = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, 
                               verbose_name="آسانی استفاده از ماسک")
    device_acceptance = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, 
                                       verbose_name="پذیرش دستگاه")
    
    # Device Information
    low_value = models.CharField(max_length=100, blank=True, null=True, verbose_name="کم")
    same_value = models.CharField(max_length=100, blank=True, null=True, verbose_name="یکسان")
    more_value = models.CharField(max_length=100, blank=True, null=True, verbose_name="بیشتر")
    ear_pressure = models.CharField(max_length=100, blank=True, null=True, verbose_name="فشار گوش")
    tap_value = models.CharField(max_length=100, blank=True, null=True, verbose_name="تپ ولر")
    joint_pain = models.CharField(max_length=100, blank=True, null=True, verbose_name="درد مفاصل")
    tired_eyes = models.CharField(max_length=100, blank=True, null=True, verbose_name="چشم های خسته")
    red_eyes = models.CharField(max_length=100, blank=True, null=True, verbose_name="چشم های قرمز")
    clear_vision = models.CharField(max_length=100, blank=True, null=True, verbose_name="دید واضح")
    dark_vision = models.CharField(max_length=100, blank=True, null=True, verbose_name="دید تیره")
    blurry_vision = models.CharField(max_length=100, blank=True, null=True, verbose_name="دید تار")
    
    # Feedback
    summary_response = models.TextField(blank=True, null=True, 
                                      verbose_name="توصیف برای دوستان")
    mask_reminder = models.TextField(blank=True, null=True, 
                                   verbose_name="ماسک یادآور چیست")
    discomfort_description = models.TextField(blank=True, null=True, 
                                            verbose_name="توضیح ناراحتی")
    mask_changes = models.TextField(blank=True, null=True, 
                                  verbose_name="تغییرات پیشنهادی")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "تیتراسیون PAP"
        verbose_name_plural = "تیتراسیون های PAP"
        ordering = ['-form_date']
    
    def __str__(self):
        return f"PAP تیتراسیون - {self.patient} - {self.form_date}"


# Form 8: Supplementary Information
class SupplementaryInformation(models.Model):
    """Form 8 - Additional medical and treatment information"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='supplementary_info')
    form_date = models.DateField(default=timezone.now, verbose_name="تاریخ فرم")
    
    # Hospitalization History
    hospitalization_history = models.TextField(blank=True, null=True, 
                                             verbose_name="سابقه بستری")
    
    # Health and Treatment Details
    health_treatment_details = models.TextField(blank=True, null=True, 
                                              verbose_name="جزئیات سلامتی و درمان")
    
    # Research Participation
    willing_participate = models.BooleanField(default=False, 
                                            verbose_name="تمایل به شرکت در تحقیقات")
    
    # Final Notes
    final_notes = models.TextField(blank=True, null=True, verbose_name="یادداشت های نهایی")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "اطلاعات تکمیلی"
        verbose_name_plural = "اطلاعات تکمیلی"
        ordering = ['-form_date']
    
    def __str__(self):
        return f"اطلاعات تکمیلی - {self.patient} - {self.form_date}"


# Medication Model for Form 8
class Medication(models.Model):
    """Medication information for supplementary form"""
    supplementary_info = models.ForeignKey(SupplementaryInformation, 
                                         on_delete=models.CASCADE, 
                                         related_name='medications')
    
    medication_name = models.CharField(max_length=200, verbose_name="نام دارو")
    quality = models.CharField(max_length=100, blank=True, null=True, 
                             verbose_name="کیفیت")
    dosage = models.CharField(max_length=100, verbose_name="مقدار مصرف")
    quantity = models.CharField(max_length=50, blank=True, null=True, 
                              verbose_name="تعداد")
    condition = models.CharField(max_length=200, verbose_name="برای چه بیماری")
    self_prescribed = models.BooleanField(default=False, verbose_name="خود مصرف")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "دارو"
        verbose_name_plural = "داروها"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.medication_name} - {self.supplementary_info.patient}"


# Treatment History Model for Form 1
class TreatmentHistory(models.Model):
    """Treatment history for patient information form"""
    patient_info = models.ForeignKey(PatientInformation, 
                                   on_delete=models.CASCADE, 
                                   related_name='treatment_histories')
    
    treatment_type = models.CharField(max_length=200, verbose_name="نوع درمان")
    start_date = models.DateField(blank=True, null=True, verbose_name="تاریخ شروع")
    end_date = models.DateField(blank=True, null=True, verbose_name="تاریخ پایان")
    result = models.TextField(blank=True, null=True, verbose_name="نتیجه")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "سابقه درمان"
        verbose_name_plural = "سوابق درمان"
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.treatment_type} - {self.patient_info.patient}"


# Sleep Study Results Model
class SleepStudyResult(models.Model):
    """Sleep study results and measurements"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, 
                              related_name='sleep_study_results')
    study_date = models.DateField(verbose_name="تاریخ مطالعه")
    physical_exam = models.ForeignKey(PhysicalExamination, 
                                    on_delete=models.SET_NULL, 
                                    null=True, blank=True,
                                    related_name='study_results')
    
    # Study Measurements
    ahi = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True,
                            verbose_name="AHI (Apnea-Hypopnea Index)")
    rdi = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True,
                            verbose_name="RDI (Respiratory Disturbance Index)")
    min_oxygen_saturation = models.IntegerField(blank=True, null=True,
                                              validators=[MinValueValidator(0), MaxValueValidator(100)],
                                              verbose_name="حداقل اشباع اکسیژن (%)")
    sleep_efficiency = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True,
                                         validators=[MinValueValidator(0), MaxValueValidator(100)],
                                         verbose_name="بازده خواب (%)")
    total_sleep_time = models.IntegerField(blank=True, null=True,
                                         verbose_name="زمان کل خواب (دقیقه)")
    
    # Study Type
    STUDY_TYPE_CHOICES = [
        ('diagnostic', 'Diagnostic'),
        ('titration', 'Titration'),
        ('split_night', 'Split Night'),
        ('home_study', 'Home Study'),
    ]
    study_type = models.CharField(max_length=20, choices=STUDY_TYPE_CHOICES,
                                verbose_name="نوع مطالعه")
    
    # Recommendations
    recommendations = models.TextField(blank=True, null=True, verbose_name="توصیه ها")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "نتیجه مطالعه خواب"
        verbose_name_plural = "نتایج مطالعات خواب"
        ordering = ['-study_date']
    
    def __str__(self):
        return f"مطالعه خواب - {self.patient} - {self.study_date}"
    
    def get_ahi_severity(self):
        """Determine AHI severity level"""
        if self.ahi is None:
            return "Unknown"
        elif self.ahi < 5:
            return "Normal"
        elif self.ahi < 15:
            return "Mild"
        elif self.ahi < 30:
            return "Moderate"
        else:
            return "Severe"
