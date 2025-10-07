from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg, Max, Min, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
from django.urls import path
from django.shortcuts import render
from django.utils import timezone


from .models import (
    Patient, PatientInformation, EpworthSleepinessScale, MedicalHistory,
    PhysicalExamination, DailySymptomAssessment, ClinicalExaminationDetails,
    PAPTitration, SupplementaryInformation, TreatmentHistory, Medication,
    SleepStudyResult
)

# Custom Admin Site
class SleepClinicAdminSite(admin.AdminSite):
    site_header = 'مرکز تشخیص و درمان اختلالات خواب'
    site_title = 'پنل مدیریت'
    index_title = 'خوش آمدید به پنل مدیریت'

# Create custom admin site instance
# sleep_clinic_admin = SleepClinicAdminSite(name='sleep_clinic_admin')


# Inline Admin Classes
class TreatmentHistoryInline(admin.TabularInline):
    model = TreatmentHistory
    extra = 1
    fields = ['treatment_type', 'start_date', 'end_date', 'result']
    verbose_name = 'سابقه درمان'
    verbose_name_plural = 'سوابق درمان'


class MedicationInline(admin.TabularInline):
    model = Medication
    extra = 1
    fields = ['medication_name', 'dosage', 'quantity', 'condition', 'self_prescribed']
    verbose_name = 'دارو'
    verbose_name_plural = 'داروها'


# Main Patient Admin
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = [
        'patient_id', 'full_name', 'national_id', 'phone', 
        'age_display', 'gender', 'bmi_display', 'created_date', 
        'forms_count', 'last_visit'
    ]
    list_filter = [
        'gender', 'created_at',
        ('birth_date', admin.DateFieldListFilter),
    ]
    search_fields = [
        'patient_id', 'first_name', 'last_name', 
        'national_id', 'phone', 'email'
    ]
    readonly_fields = [
        'bmi', 'created_at', 'updated_at', 'age_display',
        'patient_forms_summary', 'patient_actions'
    ]
    fieldsets = (
        ('اطلاعات شناسایی', {
            'fields': (
                'patient_id', ('first_name', 'last_name'), 
                'national_id', 'gender', 'birth_date', 'age_display'
            )
        }),
        ('اطلاعات تماس', {
            'fields': (
                'phone', 'email', 
                ('emergency_contact_name', 'emergency_contact_phone')
            )
        }),
        ('اندازه‌گیری‌های فیزیکی', {
            'fields': (
                ('height', 'weight', 'bmi'), 
                'neck_circumference'
            )
        }),
        ('اطلاعات سیستم', {
            'fields': (
                'created_by', 'created_at', 'updated_at',
                'patient_forms_summary', 'patient_actions'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'نام کامل'
    full_name.admin_order_field = 'first_name'
    
    def age_display(self, obj):
        if obj.birth_date:
            today = timezone.now().date()
            age = today.year - obj.birth_date.year
            if today.month < obj.birth_date.month or (today.month == obj.birth_date.month and today.day < obj.birth_date.day):
                age -= 1
            return f"{age} سال"
        return "-"
    age_display.short_description = 'سن'
    
    def bmi_display(self, obj):
        if obj.bmi:
            return format_html(
                '<span style="color: {};">{}</span>',
                self.get_bmi_color(obj.bmi),
                f"{obj.bmi:.1f}"
            )
        return "-"
    bmi_display.short_description = 'BMI'
    
    def get_bmi_color(self, bmi):
        if bmi < 18.5:
            return 'blue'
        elif bmi < 25:
            return 'green'
        elif bmi < 30:
            return 'orange'
        else:
            return 'red'
    
    def created_date(self, obj):
        return obj.created_at.strftime('%Y/%m/%d')
    created_date.short_description = 'تاریخ ثبت'
    created_date.admin_order_field = 'created_at'
    
    def forms_count(self, obj):
        total = (
            obj.information_forms.count() +
            obj.epworth_forms.count() +
            obj.medical_history_forms.count() +
            obj.physical_exams.count() +
            obj.symptom_assessments.count() +
            obj.clinical_details.count() +
            obj.pap_titrations.count() +
            obj.supplementary_info.count()
        )
        return format_html(
            '<span style="background-color: #e3f2fd; padding: 2px 8px; border-radius: 3px;">{}</span>',
            total
        )
    forms_count.short_description = 'تعداد فرم‌ها'
    
    def last_visit(self, obj):
        latest_dates = []
        
        # Check all form types for latest date
        if obj.information_forms.exists():
            latest_dates.append(obj.information_forms.latest('form_date').form_date)
        if obj.epworth_forms.exists():
            latest_dates.append(obj.epworth_forms.latest('form_date').form_date)
        if obj.medical_history_forms.exists():
            latest_dates.append(obj.medical_history_forms.latest('form_date').form_date)
        # Add other forms as needed
        
        if latest_dates:
            return max(latest_dates).strftime('%Y/%m/%d')
        return "-"
    last_visit.short_description = 'آخرین مراجعه'
    
    def patient_forms_summary(self, obj):
        summary = f"""
        <div style="background-color: #f5f5f5; padding: 10px; border-radius: 5px;">
            <h4>خلاصه فرم‌های بیمار:</h4>
            <ul style="margin: 0; padding-right: 20px;">
                <li>فرم اطلاعات بیمار: {obj.information_forms.count()} عدد</li>
                <li>مقیاس خواب‌آلودگی: {obj.epworth_forms.count()} عدد</li>
                <li>سابقه پزشکی: {obj.medical_history_forms.count()} عدد</li>
                <li>معاینات بالینی: {obj.physical_exams.count()} عدد</li>
                <li>ارزیابی علائم روزانه: {obj.symptom_assessments.count()} عدد</li>
                <li>جزئیات معاینه: {obj.clinical_details.count()} عدد</li>
                <li>تیتراسیون PAP: {obj.pap_titrations.count()} عدد</li>
                <li>اطلاعات تکمیلی: {obj.supplementary_info.count()} عدد</li>
                <li>نتایج مطالعه خواب: {obj.sleep_study_results.count()} عدد</li>
            </ul>
        </div>
        """
        return format_html(summary)
    patient_forms_summary.short_description = 'خلاصه فرم‌ها'
    
    def patient_actions(self, obj):
        return format_html(
            '<a class="button" href="/admin/sleep_clinic/patientinformation/add/?patient={}" style="margin-left: 5px;">فرم جدید</a>'
            '<a class="button" href="/sleep-clinic/patients/{}/report/" target="_blank" style="margin-left: 5px;">گزارش</a>'
            '<a class="button" href="/sleep-clinic/patients/{}/" target="_blank">مشاهده پروفایل</a>',
            obj.id, obj.id, obj.id
        )
    patient_actions.short_description = 'عملیات'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


# Patient Information Admin
@admin.register(PatientInformation)
class PatientInformationAdmin(admin.ModelAdmin):
    list_display = [
        'patient_link', 'form_date', 'symptoms_summary', 
        'has_previous_test', 'created_at'
    ]
    list_filter = [
        'form_date', 'previous_sleep_test', 'previous_apnea_diagnosis',
        'previous_pap_therapy', 'previous_surgery', 'oxygen_supplement'
    ]
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__patient_id']
    date_hierarchy = 'form_date'
    inlines = [TreatmentHistoryInline]
    raw_id_fields = ['patient']
    
    fieldsets = (
        ('اطلاعات بیمار', {
            'fields': ('patient', 'form_date')
        }),
        ('علائم', {
            'fields': (
                ('snoring', 'witnessed_apnea'),
                ('morning_confusion', 'morning_dry_mouth'),
                ('morning_nausea', 'excessive_daytime_sleepiness'),
                ('depression', 'decreased_libido')
            )
        }),
        ('سابقه مطالعات خواب', {
            'fields': (
                'previous_sleep_test',
                'previous_apnea_diagnosis',
                'previous_pap_therapy',
                'previous_surgery',
                'oxygen_supplement'
            )
        }),
        ('توضیحات', {
            'fields': ('comments',)
        })
    )
    
    def patient_link(self, obj):
        url = reverse('admin:sleep_clinic_patient_change', args=[obj.patient.id])
        return format_html('<a href="{}">{}</a>', url, obj.patient)
    patient_link.short_description = 'بیمار'
    
    def symptoms_summary(self, obj):
        symptoms = []
        if obj.snoring: symptoms.append('خرخر')
        if obj.witnessed_apnea: symptoms.append('آپنه')
        if obj.morning_confusion: symptoms.append('گیجی صبح')
        if obj.excessive_daytime_sleepiness: symptoms.append('خواب‌آلودگی')
        
        if symptoms:
            return format_html(
                '<span style="color: red;">{}</span>',
                '، '.join(symptoms[:3]) + ('...' if len(symptoms) > 3 else '')
            )
        return format_html('<span style="color: green;">بدون علامت</span>')
    symptoms_summary.short_description = 'علائم اصلی'
    
    def has_previous_test(self, obj):
        if obj.previous_sleep_test:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_previous_test.short_description = 'تست قبلی'


# Epworth Sleepiness Scale Admin
@admin.register(EpworthSleepinessScale)
class EpworthAdmin(admin.ModelAdmin):
    list_display = [
        'patient_link', 'form_date', 'total_score', 
        'score_interpretation', 'created_at'
    ]
    list_filter = [
        'form_date',
        'loud_snoring', 'wake_breathless', 'sleep_driving'
    ]
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__patient_id']
    readonly_fields = ['total_score', 'score_chart']
    date_hierarchy = 'form_date'
    
    fieldsets = (
        ('اطلاعات بیمار', {
            'fields': ('patient', 'form_date', 'total_score')
        }),
        ('سوالات مقیاس خواب‌آلودگی', {
            'fields': (
                ('sitting_reading', 'watching_tv'),
                ('sitting_inactive', 'car_passenger'),
                ('lying_down', 'sitting_talking'),
                ('after_lunch', 'in_traffic')
            ),
            'description': '0=هرگز، 1=احتمال کم، 2=احتمال متوسط، 3=احتمال زیاد'
        }),
        ('سوالات تکمیلی', {
            'fields': (
                ('loud_snoring', 'wake_breathless'),
                ('wake_tired', 'sleep_difficulty'),
                ('restful_sleep', 'unusual_behaviors'),
                ('nightmares', 'sleep_driving'),
                'other_symptoms'
            )
        }),
        ('نمودار نمرات', {
            'fields': ('score_chart',),
            'classes': ('collapse',)
        })
    )
    
    def patient_link(self, obj):
        url = reverse('admin:sleep_clinic_patient_change', args=[obj.patient.id])
        return format_html('<a href="{}">{}</a>', url, obj.patient)
    patient_link.short_description = 'بیمار'
    
    def score_interpretation(self, obj):
        if obj.total_score is None:
            return "-"
        
        score = obj.total_score
        if score < 10:
            color = 'green'
            text = 'طبیعی'
        elif score < 12:
            color = 'yellow'
            text = 'خواب‌آلودگی خفیف'
        elif score < 16:
            color = 'orange'
            text = 'خواب‌آلودگی متوسط'
        else:
            color = 'red'
            text = 'خواب‌آلودگی شدید'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            color, text
        )
    score_interpretation.short_description = 'تفسیر نمره'
    
    def score_chart(self, obj):
        if not obj.pk:
            return "ابتدا فرم را ذخیره کنید"
        
        # Get all scores for this patient
        scores = EpworthSleepinessScale.objects.filter(
            patient=obj.patient
        ).order_by('form_date').values_list('form_date', 'total_score')
        
        if scores:
            chart_data = {
                'labels': [score[0].strftime('%Y/%m/%d') for score in scores],
                'data': [score[1] for score in scores if score[1] is not None]
            }
            
            return format_html(
                '''
                <canvas id="epworth-chart" width="400" height="200"></canvas>
                <script>
                var ctx = document.getElementById('epworth-chart').getContext('2d');
                var chart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: {},
                        datasets: [{{
                            label: 'نمره Epworth',
                            data: {},
                            borderColor: 'rgb(75, 192, 192)',
                            tension: 0.1
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                max: 24
                            }}
                        }}
                    }}
                }});
                </script>
                ''',
                json.dumps(chart_data['labels']),
                json.dumps(chart_data['data'])
            )
        return "داده‌ای برای نمایش وجود ندارد"
    score_chart.short_description = 'نمودار روند نمرات'


# Medical History Admin
@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'patient_link', 'form_date', 'conditions_count', 
        'sleep_quality', 'created_at'
    ]
    list_filter = [
        'form_date', 'sleep_quality',
        'diabetes_current', 'hypertension_current', 
        'heart_problems_current', 'depression_current'
    ]
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__patient_id']
    date_hierarchy = 'form_date'
    
    fieldsets = (
        ('اطلاعات بیمار', {
            'fields': ('patient', 'form_date', 'sleep_quality')
        }),
        ('برنامه خواب', {
            'fields': (
                'sleep_thoughts', 'wake_time', 'morning_routine',
                'wake_activities', 'drowsy_activities', 
                'sleep_paralysis', 'cataplexy'
            ),
            'classes': ('collapse',)
        }),
        ('شرایط پزشکی', {
            'fields': (
                ('diabetes_current', 'diabetes_past'),
                ('hypertension_current', 'hypertension_past'),
                ('stroke_current', 'stroke_past'),
                ('heart_problems_current', 'heart_problems_past'),
                ('heart_attack_current', 'heart_attack_past'),
                ('angina_current', 'angina_past'),
                ('arrhythmia_current', 'arrhythmia_past'),
                ('asthma_current', 'asthma_past'),
                ('tuberculosis_current', 'tuberculosis_past'),
                ('lung_disease_current', 'lung_disease_past'),
                ('nasal_congestion_current', 'nasal_congestion_past'),
                ('jaw_problems_current', 'jaw_problems_past'),
                ('neurological_current', 'neurological_past'),
                ('prostate_current', 'prostate_past'),
                ('alcohol_problem_current', 'alcohol_problem_past'),
                ('addiction_current', 'addiction_past'),
                ('depression_current', 'depression_past'),
                ('fainting_current', 'fainting_past')
            )
        })
    )
    
    def patient_link(self, obj):
        url = reverse('admin:sleep_clinic_patient_change', args=[obj.patient.id])
        return format_html('<a href="{}">{}</a>', url, obj.patient)
    patient_link.short_description = 'بیمار'
    
    def conditions_count(self, obj):
        count = 0
        condition_fields = [f.name for f in obj._meta.get_fields() 
                          if f.name.endswith('_current') and getattr(obj, f.name)]
        count = len(condition_fields)
        
        if count == 0:
            return format_html('<span style="color: green;">سالم</span>')
        elif count <= 2:
            return format_html('<span style="color: orange;">{} مورد</span>', count)
        else:
            return format_html('<span style="color: red;">{} مورد</span>', count)
    conditions_count.short_description = 'تعداد بیماری‌های فعلی'


# Physical Examination Admin
@admin.register(PhysicalExamination)
class PhysicalExaminationAdmin(admin.ModelAdmin):
    list_display = [
        'patient_link', 'form_date', 'physician', 
        'study_types', 'interpreting_physician_display'
    ]
    list_filter = [
        'form_date', 'interpreting_physician',
        'baseline_diagnostic', 'full_night_titration', 
        'split_night', 're_titration', 'home_sleep_testing'
    ]
    search_fields = [
        'patient__first_name', 'patient__last_name', 
        'patient__patient_id', 'physician', 'other_physician'
    ]
    date_hierarchy = 'form_date'
    
    def patient_link(self, obj):
        url = reverse('admin:sleep_clinic_patient_change', args=[obj.patient.id])
        return format_html('<a href="{}">{}</a>', url, obj.patient)
    patient_link.short_description = 'بیمار'
    
    def study_types(self, obj):
        types = []
        if obj.baseline_diagnostic: types.append('Baseline')
        if obj.full_night_titration: types.append('Titration')
        if obj.split_night: types.append('Split')
        if obj.re_titration: types.append('Re-Titration')
        if obj.home_sleep_testing: types.append('Home')
        
        return ', '.join(types) if types else '-'
    study_types.short_description = 'نوع مطالعه'
    
    def interpreting_physician_display(self, obj):
        if obj.interpreting_physician == 'other':
            return obj.other_physician or 'نامشخص'
        return obj.get_interpreting_physician_display()
    interpreting_physician_display.short_description = 'پزشک تفسیرکننده'


# Daily Symptom Assessment Admin
@admin.register(DailySymptomAssessment)
class DailySymptomAdmin(admin.ModelAdmin):
    list_display = [
        'patient_link', 'form_date', 'total_naps', 
        'substance_use', 'symptoms_severity'
    ]
    list_filter = [
        'form_date', 'sleepiness_today', 'tiredness_today',
        'anxiety_today', 'depression_today'
    ]
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__patient_id']
    date_hierarchy = 'form_date'
    
    def patient_link(self, obj):
        url = reverse('admin:sleep_clinic_patient_change', args=[obj.patient.id])
        return format_html('<a href="{}">{}</a>', url, obj.patient)
    patient_link.short_description = 'بیمار'
    
    def total_naps(self, obj):
        total = (obj.morning_naps_count or 0) + (obj.night_naps_count or 0) + (obj.recent_naps_count or 0)
        duration = (obj.morning_naps_duration or 0) + (obj.night_naps_duration or 0) + (obj.recent_naps_duration or 0)
        return f"{total} بار / {duration} دقیقه"
    total_naps.short_description = 'مجموع چرت‌ها'
    
    def substance_use(self, obj):
        caffeine = (obj.caffeine_count_today or 0) + (obj.caffeine_count_recent or 0)
        alcohol = (obj.alcohol_count_today or 0) + (obj.alcohol_count_recent or 0)
        
        result = []
        if caffeine > 0:
            result.append(f"کافئین: {caffeine}")
        if alcohol > 0:
            result.append(f"الکل: {alcohol}")
        
        return ' | '.join(result) if result else 'هیچکدام'
    substance_use.short_description = 'مصرف مواد'
    
    def symptoms_severity(self, obj):
        severe = []
        if obj.sleepiness_today == 'more': severe.append('خواب‌آلودگی')
        if obj.tiredness_today == 'more': severe.append('خستگی')
        if obj.anxiety_today == 'more': severe.append('اضطراب')
        if obj.depression_today == 'more': severe.append('افسردگی')
        
        if severe:
            return format_html(
                '<span style="color: red;">{}</span>',
                '، '.join(severe)
            )
        return format_html('<span style="color: green;">عادی</span>')
    symptoms_severity.short_description = 'علائم شدید'


# Clinical Examination Details Admin
@admin.register(ClinicalExaminationDetails)
class ClinicalDetailsAdmin(admin.ModelAdmin):
    list_display = [
        'patient_link', 'form_date', 'sleep_schedule_summary',
        'shift_work', 'clinical_findings_count'
    ]
    list_filter = [
        'form_date', 'shift_work',
        'loud_snoring', 'witnessed_apnea', 'sleep_walking'
    ]
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__patient_id']
    date_hierarchy = 'form_date'
    
    fieldsets = (
        ('اطلاعات بیمار', {
            'fields': ('patient', 'form_date')
        }),
        ('برنامه خواب', {
            'fields': (
                ('weekday_bedtime', 'weekday_waketime'),
                ('weekend_bedtime', 'weekend_waketime'),
                'shift_work', 'shift_work_description'
            )
        }),
        ('معاینه گلو', {
            'fields': (
                'small_mouth_throat', 'small_mouth_soft_palate',
                'normal_mouth_soft_palate', 'normal_mouth_visible_uvula',
                'normal_mouth_visible_tonsils', 'mouth_with_large_tonsils',
                'large_tongue'
            )
        }),
        ('معاینه بینی', {
            'fields': (
                'nasal_congestion_right', 'nasal_congestion_left',
                'nasal_deviation'
            )
        }),
        ('علائم اضافی', {
            'fields': (
                'loud_snoring', 'choking_episodes', 'witnessed_apnea',
                'restless_sleep', 'sleep_walking', 'night_terrors',
                'morning_headaches', 'dry_mouth', 'nightmares'
            )
        })
    )
    
    def patient_link(self, obj):
        url = reverse('admin:sleep_clinic_patient_change', args=[obj.patient.id])
        return format_html('<a href="{}">{}</a>', url, obj.patient)
    patient_link.short_description = 'بیمار'
    
    def sleep_schedule_summary(self, obj):
        if obj.weekday_bedtime and obj.weekday_waketime:
            return f"هفته: {obj.weekday_bedtime.strftime('%H:%M')} - {obj.weekday_waketime.strftime('%H:%M')}"
        return "-"
    sleep_schedule_summary.short_description = 'برنامه خواب'
    
    def clinical_findings_count(self, obj):
        count = 0
        findings = [
            'small_mouth_throat', 'large_tongue', 'nasal_congestion_right',
            'nasal_congestion_left', 'loud_snoring', 'witnessed_apnea',
            'sleep_walking', 'morning_headaches'
        ]
        count = sum(1 for f in findings if getattr(obj, f, False))
        
        if count == 0:
            return format_html('<span style="color: green;">طبیعی</span>')
        elif count <= 3:
            return format_html('<span style="color: orange;">{} یافته</span>', count)
        else:
            return format_html('<span style="color: red;">{} یافته</span>', count)
    clinical_findings_count.short_description = 'یافته‌های بالینی'


# PAP Titration Admin
@admin.register(PAPTitration)
class PAPTitrationAdmin(admin.ModelAdmin):
    list_display = [
        'patient_link', 'form_date', 'morning_feeling',
        'therapy_effectiveness', 'acceptance_summary'
    ]
    list_filter = [
        'form_date', 'morning_feeling', 
        'pap_improvement', 'mask_ease', 'device_acceptance'
    ]
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__patient_id']
    date_hierarchy = 'form_date'
    
    def patient_link(self, obj):
        url = reverse('admin:sleep_clinic_patient_change', args=[obj.patient.id])
        return format_html('<a href="{}">{}</a>', url, obj.patient)
    patient_link.short_description = 'بیمار'
    
    def therapy_effectiveness(self, obj):
        if obj.pap_improvement in ['good', 'excellent']:
            return format_html('<span style="color: green;">✓ موثر</span>')
        elif obj.pap_improvement in ['moderate']:
            return format_html('<span style="color: orange;">~ متوسط</span>')
        else:
            return format_html('<span style="color: red;">✗ ناموثر</span>')
    therapy_effectiveness.short_description = 'اثربخشی درمان'
    
    def acceptance_summary(self, obj):
        scores = {
            'excellent': 5, 'good': 4, 'moderate': 3, 
            'little': 2, 'none': 1
        }
        
        # Calculate average acceptance
        total = 0
        count = 0
        for field in ['pap_improvement', 'mask_ease', 'device_acceptance']:
            value = getattr(obj, field, None)
            if value and value in scores:
                total += scores[value]
                count += 1
        
        if count > 0:
            avg = total / count
            if avg >= 4:
                return format_html('<span style="color: green;">عالی</span>')
            elif avg >= 3:
                return format_html('<span style="color: orange;">قابل قبول</span>')
            else:
                return format_html('<span style="color: red;">ضعیف</span>')
        return "-"
    acceptance_summary.short_description = 'پذیرش کلی'


# Supplementary Information Admin
@admin.register(SupplementaryInformation)
class SupplementaryInfoAdmin(admin.ModelAdmin):
    list_display = [
        'patient_link', 'form_date', 'has_hospitalization',
        'medications_count', 'willing_participate'
    ]
    list_filter = ['form_date', 'willing_participate']
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__patient_id']
    date_hierarchy = 'form_date'
    inlines = [MedicationInline]
    
    def patient_link(self, obj):
        url = reverse('admin:sleep_clinic_patient_change', args=[obj.patient.id])
        return format_html('<a href="{}">{}</a>', url, obj.patient)
    patient_link.short_description = 'بیمار'
    
    def has_hospitalization(self, obj):
        if obj.hospitalization_history:
            return format_html('<span style="color: red;">✓</span>')
        return format_html('<span style="color: green;">✗</span>')
    has_hospitalization.short_description = 'سابقه بستری'
    
    def medications_count(self, obj):
        count = obj.medications.count()
        if count == 0:
            return format_html('<span style="color: green;">بدون دارو</span>')
        elif count <= 3:
            return format_html('<span style="color: orange;">{} دارو</span>', count)
        else:
            return format_html('<span style="color: red;">{} دارو</span>', count)
    medications_count.short_description = 'تعداد داروها'


# Sleep Study Result Admin
@admin.register(SleepStudyResult)
class SleepStudyResultAdmin(admin.ModelAdmin):
    list_display = [
        'patient_link', 'study_date', 'study_type',
        'ahi_display', 'severity_display', 'oxygen_display',
        'sleep_efficiency_display'
    ]
    list_filter = [
        'study_date', 'study_type',
    ]
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__patient_id']
    date_hierarchy = 'study_date'
    
    fieldsets = (
        ('اطلاعات مطالعه', {
            'fields': ('patient', 'study_date', 'study_type', 'physical_exam')
        }),
        ('نتایج مطالعه', {
            'fields': (
                ('ahi', 'rdi'),
                ('min_oxygen_saturation', 'sleep_efficiency'),
                'total_sleep_time'
            )
        }),
        ('توصیه‌ها', {
            'fields': ('recommendations',)
        })
    )
    
    def patient_link(self, obj):
        url = reverse('admin:sleep_clinic_patient_change', args=[obj.patient.id])
        return format_html('<a href="{}">{}</a>', url, obj.patient)
    patient_link.short_description = 'بیمار'
    
    def ahi_display(self, obj):
        if obj.ahi is not None:
            return format_html(
                '<span style="font-weight: bold;">{}</span>',
                f"{obj.ahi:.1f}"
            )
        return "-"
    ahi_display.short_description = 'AHI'
    ahi_display.admin_order_field = 'ahi'
    
    def severity_display(self, obj):
        severity = obj.get_ahi_severity()
        colors = {
            'Normal': 'green',
            'Mild': 'yellow',
            'Moderate': 'orange',
            'Severe': 'red',
            'Unknown': 'gray'
        }
        persian_labels = {
            'Normal': 'طبیعی',
            'Mild': 'خفیف',
            'Moderate': 'متوسط',
            'Severe': 'شدید',
            'Unknown': 'نامشخص'
        }
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            colors.get(severity, 'gray'),
            persian_labels.get(severity, severity)
        )
    severity_display.short_description = 'شدت'
    
    def oxygen_display(self, obj):
        if obj.min_oxygen_saturation is not None:
            color = 'green' if obj.min_oxygen_saturation >= 90 else 'red'
            return format_html(
                '<span style="color: {};">{} %</span>',
                color, obj.min_oxygen_saturation
            )
        return "-"
    oxygen_display.short_description = 'حداقل اکسیژن'
    oxygen_display.admin_order_field = 'min_oxygen_saturation'
    
    def sleep_efficiency_display(self, obj):
        if obj.sleep_efficiency is not None:
            color = 'green' if obj.sleep_efficiency >= 85 else 'orange'
            return format_html(
                '<span style="color: {};">{} %</span>',
                color, f"{obj.sleep_efficiency:.1f}"
            )
        return "-"
    sleep_efficiency_display.short_description = 'بازده خواب'
    sleep_efficiency_display.admin_order_field = 'sleep_efficiency'


# Treatment History Admin (if needed separately)
@admin.register(TreatmentHistory)
class TreatmentHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'patient_name', 'treatment_type', 'start_date', 
        'end_date', 'duration_days', 'has_result'
    ]
    list_filter = ['start_date', 'end_date']
    search_fields = [
        'patient_info__patient__first_name',
        'patient_info__patient__last_name',
        'treatment_type'
    ]
    date_hierarchy = 'start_date'
    
    def patient_name(self, obj):
        patient = obj.patient_info.patient
        url = reverse('admin:sleep_clinic_patient_change', args=[patient.id])
        return format_html('<a href="{}">{}</a>', url, patient)
    patient_name.short_description = 'بیمار'
    
    def duration_days(self, obj):
        if obj.start_date and obj.end_date:
            delta = obj.end_date - obj.start_date
            return f"{delta.days} روز"
        return "-"
    duration_days.short_description = 'مدت درمان'
    
    def has_result(self, obj):
        if obj.result:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: gray;">-</span>')
    has_result.short_description = 'نتیجه'


# Medication Admin (if needed separately)
@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = [
        'patient_name', 'medication_name', 'dosage', 
        'quantity', 'condition', 'self_prescribed'
    ]
    list_filter = ['self_prescribed', 'created_at']
    search_fields = [
        'supplementary_info__patient__first_name',
        'supplementary_info__patient__last_name',
        'medication_name', 'condition'
    ]
    
    def patient_name(self, obj):
        patient = obj.supplementary_info.patient
        url = reverse('admin:sleep_clinic_patient_change', args=[patient.id])
        return format_html('<a href="{}">{}</a>', url, patient)
    patient_name.short_description = 'بیمار'


# Custom Admin Dashboard


def sleep_clinic_dashboard(request):
    """Custom dashboard for sleep clinic statistics"""
    
    # Get date range (last 30 days)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Statistics
    context = {
        'title': 'داشبورد مرکز خواب',
        
        # Patient Statistics
        'total_patients': Patient.objects.count(),
        'new_patients_month': Patient.objects.filter(
            created_at__date__gte=start_date
        ).count(),
        
        # Form Statistics
        'total_forms': {
            'patient_info': PatientInformation.objects.count(),
            'epworth': EpworthSleepinessScale.objects.count(),
            'medical_history': MedicalHistory.objects.count(),
            'studies': SleepStudyResult.objects.count(),
        },
        
        # Epworth Statistics
        'epworth_avg': EpworthSleepinessScale.objects.aggregate(
            Avg('total_score')
        )['total_score__avg'] or 0,
        
        'epworth_distribution': {
            'normal': EpworthSleepinessScale.objects.filter(
                total_score__lt=10
            ).count(),
            'mild': EpworthSleepinessScale.objects.filter(
                total_score__gte=10, total_score__lt=12
            ).count(),
            'moderate': EpworthSleepinessScale.objects.filter(
                total_score__gte=12, total_score__lt=16
            ).count(),
            'severe': EpworthSleepinessScale.objects.filter(
                total_score__gte=16
            ).count(),
        },
        
        # AHI Statistics
        'ahi_distribution': {
            'normal': SleepStudyResult.objects.filter(ahi__lt=5).count(),
            'mild': SleepStudyResult.objects.filter(
                ahi__gte=5, ahi__lt=15
            ).count(),
            'moderate': SleepStudyResult.objects.filter(
                ahi__gte=15, ahi__lt=30
            ).count(),
            'severe': SleepStudyResult.objects.filter(ahi__gte=30).count(),
        },
        
        # Recent Activities
        'recent_patients': Patient.objects.order_by('-created_at')[:5],
        'recent_studies': SleepStudyResult.objects.select_related(
            'patient'
        ).order_by('-study_date')[:5],
    }
    
    return render(request, 'admin/sleep_clinic_dashboard.html', context)


# Add custom URLs to admin
class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('sleep-clinic-dashboard/', 
                 self.admin_view(sleep_clinic_dashboard), 
                 name='sleep_clinic_dashboard'),
        ]
        return custom_urls + urls

# Uncomment to use custom admin site
# admin_site = CustomAdminSite(name='custom_admin')


# Admin customization for better UX
admin.site.site_header = 'مرکز تشخیص و درمان اختلالات خواب'
admin.site.site_title = 'پنل مدیریت مرکز خواب'
admin.site.index_title = 'مدیریت بیماران و فرم‌ها'


# Custom CSS for admin (save as static/admin/css/custom_admin.css)
"""
/* RTL Support for Admin */
body.rtl {
    direction: rtl;
    text-align: right;
}

/* Custom styles for sleep clinic admin */
.module h2 {
    background-color: #8BC34A;
}

.button, input[type=submit], input[type=button], .submit-row input {
    background-color: #8BC34A;
}

.button:hover, input[type=submit]:hover {
    background-color: #689F38;
}

/* Score badges */
.score-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 3px;
    font-weight: bold;
}

/* Custom dashboard styles */
.dashboard-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.stat-card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    text-align: center;
}

.stat-card h3 {
    margin: 0;
    font-size: 2em;
    color: #8BC34A;
}

.stat-card p {
    margin: 5px 0 0;
    color: #666;
}
"""