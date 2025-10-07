from django import forms
from django.forms import modelformset_factory, inlineformset_factory
from django.core.exceptions import ValidationError
from datetime import date

from .models import (
    Patient, PatientInformation, EpworthSleepinessScale, MedicalHistory,
    PhysicalExamination, DailySymptomAssessment, ClinicalExaminationDetails,
    PAPTitration, SupplementaryInformation, TreatmentHistory, Medication,SleepStudyResult
)


# Base form classes with Persian labels and RTL support
class PersianModelForm(forms.ModelForm):
    """Base form with RTL support and Persian error messages"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add RTL CSS class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['dir'] = 'rtl'
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += ' form-control-rtl'
            else:
                field.widget.attrs['class'] = 'form-control form-control-rtl'


# Patient Form
class PatientForm(PersianModelForm):
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='تاریخ تولد'
    )
    
    class Meta:
        model = Patient
        fields = [
            'patient_id', 'first_name', 'last_name', 'national_id',
            'phone', 'email', 'emergency_contact_name', 'emergency_contact_phone',
            'gender', 'birth_date', 'height', 'weight', 'neck_circumference'
        ]
        
    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        if national_id and len(national_id) != 10:
            raise ValidationError('کد ملی باید 10 رقم باشد')
        return national_id
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.startswith('09'):
            raise ValidationError('شماره موبایل باید با 09 شروع شود')
        return phone


# Form 1: Patient Information Form
class PatientInformationForm(PersianModelForm):
    class Meta:
        model = PatientInformation
        exclude = ['patient', 'created_at', 'updated_at']
        widgets = {
            'form_date': forms.DateInput(attrs={'type': 'date'}),
            'comments': forms.Textarea(attrs={'rows': 4}),
        }


# Form 2: Epworth Sleepiness Scale Form
class EpworthForm(PersianModelForm):
    class Meta:
        model = EpworthSleepinessScale
        exclude = ['patient', 'total_score', 'created_at', 'updated_at']
        widgets = {
            'form_date': forms.DateInput(attrs={'type': 'date'}),
            'other_symptoms': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom CSS classes for ESS radio buttons
        ess_fields = [
            'sitting_reading', 'watching_tv', 'sitting_inactive', 
            'car_passenger', 'lying_down', 'sitting_talking', 
            'after_lunch', 'in_traffic'
        ]
        for field in ess_fields:
            self.fields[field].widget = forms.RadioSelect()
            self.fields[field].widget.attrs['class'] = 'ess-radio'


# Form 3: Medical History Form
class MedicalHistoryForm(PersianModelForm):
    class Meta:
        model = MedicalHistory
        exclude = ['patient', 'created_at', 'updated_at']
        widgets = {
            'form_date': forms.DateInput(attrs={'type': 'date'}),
            'sleep_thoughts': forms.Textarea(attrs={'rows': 3}),
            'wake_time': forms.Textarea(attrs={'rows': 3}),
            'morning_routine': forms.Textarea(attrs={'rows': 3}),
            'wake_activities': forms.Textarea(attrs={'rows': 3}),
            'drowsy_activities': forms.Textarea(attrs={'rows': 3}),
            'sleep_paralysis': forms.Textarea(attrs={'rows': 3}),
            'cataplexy': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Group medical conditions
        condition_fields = [f for f in self.fields if f.endswith('_current') or f.endswith('_past')]
        for field in condition_fields:
            self.fields[field].widget.attrs['class'] = 'form-check-input'


# Form 4: Physical Examination Form
class PhysicalExaminationForm(PersianModelForm):
    class Meta:
        model = PhysicalExamination
        exclude = ['patient', 'created_at', 'updated_at']
        widgets = {
            'form_date': forms.DateInput(attrs={'type': 'date'}),
            'interpreting_physician': forms.RadioSelect(),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        interpreting_physician = cleaned_data.get('interpreting_physician')
        other_physician = cleaned_data.get('other_physician')
        
        if interpreting_physician == 'other' and not other_physician:
            raise ValidationError({
                'other_physician': 'لطفا نام پزشک را وارد کنید'
            })
        return cleaned_data


# Form 5: Daily Symptom Assessment Form
class DailySymptomForm(PersianModelForm):
    class Meta:
        model = DailySymptomAssessment
        exclude = ['patient', 'created_at', 'updated_at']
        widgets = {
            'form_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add radio button styling for comparison fields
        comparison_fields = [
            'sleepiness_today', 'tiredness_today', 'physical_activity',
            'feeling_sick', 'anxiety_today', 'depression_today', 'sleepy_now'
        ]
        for field in comparison_fields:
            self.fields[field].widget = forms.RadioSelect()
            self.fields[field].widget.attrs['class'] = 'comparison-radio'


# Form 6: Clinical Examination Details Form
class ClinicalDetailsForm(PersianModelForm):
    class Meta:
        model = ClinicalExaminationDetails
        exclude = ['patient', 'created_at', 'updated_at']
        widgets = {
            'form_date': forms.DateInput(attrs={'type': 'date'}),
            'weekday_bedtime': forms.TimeInput(attrs={'type': 'time'}),
            'weekday_waketime': forms.TimeInput(attrs={'type': 'time'}),
            'weekend_bedtime': forms.TimeInput(attrs={'type': 'time'}),
            'weekend_waketime': forms.TimeInput(attrs={'type': 'time'}),
            'shift_work_description': forms.Textarea(attrs={'rows': 3}),
        }


# Form 7: PAP Titration Form
class PAPTitrationForm(PersianModelForm):
    class Meta:
        model = PAPTitration
        exclude = ['patient', 'created_at', 'updated_at']
        widgets = {
            'form_date': forms.DateInput(attrs={'type': 'date'}),
            'morning_feeling': forms.RadioSelect(),
            'pap_improvement': forms.RadioSelect(),
            'mask_ease': forms.RadioSelect(),
            'device_acceptance': forms.RadioSelect(),
            'summary_response': forms.Textarea(attrs={'rows': 4}),
            'mask_reminder': forms.Textarea(attrs={'rows': 3}),
            'discomfort_description': forms.Textarea(attrs={'rows': 4}),
            'mask_changes': forms.Textarea(attrs={'rows': 4}),
        }


# Form 8: Supplementary Information Form
class SupplementaryInfoForm(PersianModelForm):
    class Meta:
        model = SupplementaryInformation
        exclude = ['patient', 'created_at', 'updated_at']
        widgets = {
            'form_date': forms.DateInput(attrs={'type': 'date'}),
            'hospitalization_history': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'لطفا جزئیات مربوط به بستری های قبلی خود را با ذکر تاریخ، مدت بستری و دلیل آن وارد نمایید...'
            }),
            'health_treatment_details': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'داروهای مصرفی، درمان های در حال انجام، مشکلات خاص سلامتی و سایر موارد مهم را ذکر کنید...'
            }),
            'final_notes': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'توضیحات تکمیلی...'
            }),
        }


# Formsets for related models
TreatmentHistoryFormSet = inlineformset_factory(
    PatientInformation,
    TreatmentHistory,
    fields=['treatment_type', 'start_date', 'end_date', 'result'],
    extra=3,
    can_delete=True,
    widgets={
        'start_date': forms.DateInput(attrs={'type': 'date'}),
        'end_date': forms.DateInput(attrs={'type': 'date'}),
        'result': forms.Textarea(attrs={'rows': 2}),
    }
)

MedicationFormSet = inlineformset_factory(
    SupplementaryInformation,
    Medication,
    fields=['medication_name', 'quality', 'dosage', 'quantity', 'condition', 'self_prescribed'],
    extra=5,
    can_delete=True,
    widgets={
        'medication_name': forms.TextInput(attrs={'placeholder': 'نام دارو'}),
        'quality': forms.TextInput(attrs={'placeholder': 'کیفیت'}),
        'dosage': forms.TextInput(attrs={'placeholder': 'مقدار مصرف'}),
        'quantity': forms.TextInput(attrs={'placeholder': 'تعداد'}),
        'condition': forms.TextInput(attrs={'placeholder': 'برای چه بیماری'}),
    }
)


# Custom form for patient search
class PatientSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'جستجو بر اساس نام، نام خانوادگی، شناسه بیمار یا کد ملی...',
            'dir': 'rtl'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='از تاریخ'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='تا تاریخ'
    )


# Form for creating new patient with initial assessment
class NewPatientAssessmentForm(forms.Form):
    """Combined form for creating new patient and initial assessment"""
    
    # Patient fields
    patient_id = forms.CharField(max_length=20, label='شناسه بیمار')
    first_name = forms.CharField(max_length=100, label='نام')
    last_name = forms.CharField(max_length=100, label='نام خانوادگی')
    national_id = forms.CharField(max_length=10, required=False, label='کد ملی')
    phone = forms.CharField(max_length=15, label='تلفن همراه')
    email = forms.EmailField(required=False, label='پست الکترونیکی')
    gender = forms.ChoiceField(choices=Patient.GENDER_CHOICES, label='جنسیت')
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='تاریخ تولد'
    )
    height = forms.IntegerField(min_value=50, max_value=250, label='قد (سانتی متر)')
    weight = forms.DecimalField(min_value=20, max_value=300, label='وزن (کیلوگرم)')
    
    # Initial symptoms
    chief_complaint = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        label='شکایت اصلی'
    )
    symptom_duration = forms.CharField(
        max_length=100,
        label='مدت زمان علائم'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['dir'] = 'rtl'
            field.widget.attrs['class'] = 'form-control'


# Form for sleep study results
class SleepStudyResultForm(PersianModelForm):
    class Meta:
        model = SleepStudyResult
        exclude = ['created_at', 'updated_at']
        widgets = {
            'study_date': forms.DateInput(attrs={'type': 'date'}),
            'recommendations': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        ahi = cleaned_data.get('ahi')
        min_oxygen = cleaned_data.get('min_oxygen_saturation')
        
        # Validate AHI and oxygen values
        if ahi is not None and ahi < 0:
            raise ValidationError({'ahi': 'AHI نمی تواند منفی باشد'})
        
        if min_oxygen is not None and (min_oxygen < 0 or min_oxygen > 100):
            raise ValidationError({
                'min_oxygen_saturation': 'اشباع اکسیژن باید بین 0 تا 100 باشد'
            })
        
        return cleaned_data


# Form validators
def validate_persian_name(value):
    """Validate that name contains only Persian characters"""
    import re
    if not re.match(r'^[\u0600-\u06FF\s]+, value'):
        raise ValidationError('لطفا فقط از حروف فارسی استفاده کنید')


def validate_future_date(value):
    """Validate that date is not in the future"""
    if value > date.today():
        raise ValidationError('تاریخ نمی تواند در آینده باشد')


# Custom widget for time selection with Persian numbers
class PersianTimeWidget(forms.TimeInput):
    """Custom time widget with Persian number support"""
    
    def __init__(self, attrs=None):
        default_attrs = {'type': 'time', 'dir': 'ltr'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


# Form for bulk patient import
class BulkPatientImportForm(forms.Form):
    csv_file = forms.FileField(
        label='فایل CSV',
        help_text='فایل CSV حاوی اطلاعات بیماران'
    )
    
    def clean_csv_file(self):
        file = self.cleaned_data['csv_file']
        if not file.name.endswith('.csv'):
            raise ValidationError('فقط فایل های CSV مجاز هستند')
        
        # Check file size (max 5MB)
        if file.size > 5 * 1024 * 1024:
            raise ValidationError('حجم فایل نباید بیشتر از 5 مگابایت باشد')
        
        return file