from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.db import transaction,models
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime, date
import json

from .models import (
    Patient, PatientInformation, EpworthSleepinessScale, MedicalHistory,
    PhysicalExamination, DailySymptomAssessment, ClinicalExaminationDetails,
    PAPTitration, SupplementaryInformation, TreatmentHistory, Medication,
    SleepStudyResult
)
from .forms import (
    PatientForm, PatientInformationForm, EpworthForm, MedicalHistoryForm,
    PhysicalExaminationForm, DailySymptomForm, ClinicalDetailsForm,
    PAPTitrationForm, SupplementaryInfoForm, TreatmentHistoryFormSet,
    MedicationFormSet
)


# Base Views
@login_required
def dashboard(request):
    """Main dashboard view showing patient statistics and recent activities"""
    context = {
        'total_patients': Patient.objects.count(),
        'recent_patients': Patient.objects.order_by('-created_at')[:5],
        'pending_studies': PhysicalExamination.objects.filter(
            study_results__isnull=True
        ).count(),
        'recent_studies': SleepStudyResult.objects.order_by('-study_date')[:5],
        'active_form': 'dashboard',
    }
    return render(request, 'sleep_clinic/dashboard.html', context)


@login_required
def patient_list(request):
    """List all patients with search and pagination"""
    patients = Patient.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        patients = patients.filter(
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(patient_id__icontains=search_query) |
            models.Q(national_id__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(patients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'patients': page_obj,
        'search_query': search_query,
        'active_form': 'patients',
    }
    return render(request, 'sleep_clinic/patient_list.html', context)


@login_required
def patient_detail(request, patient_id):
    """Detailed view of a patient with all their forms and studies"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    context = {
        'patient': patient,
        'information_forms': patient.information_forms.all(),
        'epworth_forms': patient.epworth_forms.all(),
        'medical_histories': patient.medical_history_forms.all(),
        'physical_exams': patient.physical_exams.all(),
        'symptom_assessments': patient.symptom_assessments.all(),
        'clinical_details': patient.clinical_details.all(),
        'pap_titrations': patient.pap_titrations.all(),
        'supplementary_info': patient.supplementary_info.all(),
        'study_results': patient.sleep_study_results.all(),
        'active_form': 'patients',
    }
    return render(request, 'sleep_clinic/patient_detail.html', context)


# Form 1: Patient Information
@login_required
@transaction.atomic
def form1_create(request, patient_id=None):
    """Create or update Form 1 - Patient Information"""
    patient = None
    if patient_id:
        patient = get_object_or_404(Patient, id=patient_id)
    
    if request.method == 'POST':
        # Handle patient creation/update if needed
        if not patient:
            patient_form = PatientForm(request.POST)
            if patient_form.is_valid():
                patient = patient_form.save(commit=False)
                patient.created_by = request.user
                patient.save()
            else:
                messages.error(request, 'خطا در ثبت اطلاعات بیمار')
                return render(request, 'sleep_clinic/form1.html', {
                    'patient_form': patient_form,
                    'active_form': 'form1',
                })
        
        # Create patient information form
        info_form = PatientInformationForm(request.POST)
        if info_form.is_valid():
            patient_info = info_form.save(commit=False)
            patient_info.patient = patient
            patient_info.save()
            
            # Handle treatment history formset
            treatment_formset = TreatmentHistoryFormSet(
                request.POST, 
                instance=patient_info
            )
            if treatment_formset.is_valid():
                treatment_formset.save()
            
            messages.success(request, 'اطلاعات بیمار با موفقیت ثبت شد')
            
            # Redirect to next form
            return redirect('form2', patient_id=patient.id)
        else:
            messages.error(request, 'خطا در ثبت فرم')
    else:
        patient_form = PatientForm(instance=patient) if patient else PatientForm()
        info_form = PatientInformationForm()
        treatment_formset = TreatmentHistoryFormSet()
    
    context = {
        'patient': patient,
        'patient_form': patient_form if not patient else None,
        'form': info_form,
        'treatment_formset': treatment_formset,
        'active_form': 'form1',
    }
    return render(request, 'sleep_clinic/form1.html', context)


# Form 2: Epworth Sleepiness Scale
@login_required
def form2_create(request, patient_id=None):
    """Create Form 2 - Epworth Sleepiness Scale"""
    #patient = get_object_or_404(Patient, id=patient_id)
    patient = None
    if request.method == 'POST':
        form = EpworthForm(request.POST)
        if form.is_valid():
            epworth = form.save(commit=False)
            epworth.patient = patient
            epworth.save()
            
            messages.success(request, 'مقیاس خواب آلودگی اپورث با موفقیت ثبت شد')
            return redirect('form3', patient_id=patient.id)
        else:
            messages.error(request, 'خطا در ثبت فرم')
    else:
        form = EpworthForm()
    
    context = {
        'patient': patient,
        'form': form,
        'active_form': 'form2',
    }
    return render(request, 'sleep_clinic/form2.html', context)


# Form 3: Medical History
@login_required
def form3_create(request, patient_id=None):
    """Create Form 3 - Medical History"""
    #patient = get_object_or_404(Patient, id=patient_id)
    patient = None
    if request.method == 'POST':
        form = MedicalHistoryForm(request.POST)
        if form.is_valid():
            medical_history = form.save(commit=False)
            medical_history.patient = patient
            medical_history.save()
            
            messages.success(request, 'سابقه پزشکی با موفقیت ثبت شد')
            return redirect('form4', patient_id=patient.id)
        else:
            messages.error(request, 'خطا در ثبت فرم')
    else:
        form = MedicalHistoryForm()
    
    context = {
        'patient': patient,
        'form': form,
        'active_form': 'form3',
    }
    return render(request, 'sleep_clinic/form3.html', context)


# Form 4: Physical Examination
@login_required
def form4_create(request, patient_id=None):
    """Create Form 4 - Physical Examination"""
    #patient = get_object_or_404(Patient, id=patient_id)
    patient = None 
    if request.method == 'POST':
        form = PhysicalExaminationForm(request.POST)
        if form.is_valid():
            physical_exam = form.save(commit=False)
            physical_exam.patient = patient
            physical_exam.save()
            
            messages.success(request, 'معاینات بالینی با موفقیت ثبت شد')
            return redirect('form5', patient_id=patient.id)
        else:
            messages.error(request, 'خطا در ثبت فرم')
    else:
        form = PhysicalExaminationForm()
    
    context = {
        'patient': patient,
        'form': form,
        'active_form': 'form4',
    }
    return render(request, 'sleep_clinic/form4.html', context)


# Form 5: Daily Symptom Assessment
@login_required
def form5_create(request, patient_id=None):
    """Create Form 5 - Daily Symptom Assessment"""
    #patient = get_object_or_404(Patient, id=patient_id)
    patient = None
    if request.method == 'POST':
        form = DailySymptomForm(request.POST)
        if form.is_valid():
            symptom_assessment = form.save(commit=False)
            symptom_assessment.patient = patient
            symptom_assessment.save()
            
            messages.success(request, 'ارزیابی علائم روزانه با موفقیت ثبت شد')
            return redirect('form6', patient_id=patient.id)
        else:
            messages.error(request, 'خطا در ثبت فرم')
    else:
        form = DailySymptomForm()
    
    context = {
        'patient': patient,
        'form': form,
        'active_form': 'form5',
    }
    return render(request, 'sleep_clinic/form5.html', context)


# Form 6: Clinical Examination Details
@login_required
def form6_create(request, patient_id=None):
    """Create Form 6 - Clinical Examination Details"""
    #patient = get_object_or_404(Patient, id=patient_id)
    patient = None
    if request.method == 'POST':
        form = ClinicalDetailsForm(request.POST)
        if form.is_valid():
            clinical_details = form.save(commit=False)
            clinical_details.patient = patient
            clinical_details.save()
            
            messages.success(request, 'جزئیات معاینه بالینی با موفقیت ثبت شد')
            return redirect('form7', patient_id=patient.id)
        else:
            messages.error(request, 'خطا در ثبت فرم')
    else:
        form = ClinicalDetailsForm()
    
    context = {
        'patient': patient,
        'form': form,
        'active_form': 'form6',
    }
    return render(request, 'sleep_clinic/form6.html', context)


# Form 7: PAP Titration
@login_required
def form7_create(request, patient_id=None):
    """Create Form 7 - PAP Titration"""
    #patient = get_object_or_404(Patient, id=patient_id)
    patient = None
    if request.method == 'POST':
        form = PAPTitrationForm(request.POST)
        if form.is_valid():
            pap_titration = form.save(commit=False)
            pap_titration.patient = patient
            pap_titration.save()
            
            messages.success(request, 'فرم PAP تیتراسیون با موفقیت ثبت شد')
            return redirect('form8', patient_id=patient.id)
        else:
            messages.error(request, 'خطا در ثبت فرم')
    else:
        form = PAPTitrationForm()
    
    context = {
        'patient': patient,
        'form': form,
        'active_form': 'form7',
    }
    return render(request, 'sleep_clinic/form7.html', context)


# Form 8: Supplementary Information
@login_required
@transaction.atomic
def form8_create(request, patient_id=None):
    """Create Form 8 - Supplementary Information"""
    #patient = get_object_or_404(Patient, id=patient_id)
    patient = None
    if request.method == 'POST':
        form = SupplementaryInfoForm(request.POST)
        if form.is_valid():
            supplementary_info = form.save(commit=False)
            supplementary_info.patient = patient
            supplementary_info.save()
            
            # Handle medication formset
            medication_formset = MedicationFormSet(
                request.POST,
                instance=supplementary_info
            )
            if medication_formset.is_valid():
                medication_formset.save()
            
            messages.success(request, 'اطلاعات تکمیلی با موفقیت ثبت شد')
            return redirect('patient_detail', patient_id=patient.id)
        else:
            messages.error(request, 'خطا در ثبت فرم')
            medication_formset = MedicationFormSet(request.POST)
    else:
        form = SupplementaryInfoForm()
        medication_formset = MedicationFormSet()
    
    context = {
        'patient': patient,
        'form': form,
        'medication_formset': medication_formset,
        'active_form': 'form8',
    }
    return render(request, 'sleep_clinic/form8.html', context)


# Update Views for existing forms
@login_required
def form1_update(request, patient_id, form_id):
    """Update existing Form 1"""
    patient = get_object_or_404(Patient, id=patient_id)
    patient_info = get_object_or_404(PatientInformation, id=form_id, patient=patient)
    
    if request.method == 'POST':
        form = PatientInformationForm(request.POST, instance=patient_info)
        treatment_formset = TreatmentHistoryFormSet(
            request.POST,
            instance=patient_info
        )
        
        if form.is_valid() and treatment_formset.is_valid():
            form.save()
            treatment_formset.save()
            messages.success(request, 'اطلاعات بیمار با موفقیت بروزرسانی شد')
            return redirect('patient_detail', patient_id=patient.id)
    else:
        form = PatientInformationForm(instance=patient_info)
        treatment_formset = TreatmentHistoryFormSet(instance=patient_info)
    
    context = {
        'patient': patient,
        'form': form,
        'treatment_formset': treatment_formset,
        'active_form': 'form1',
        'is_update': True,
    }
    return render(request, 'sleep_clinic/form1.html', context)


# Similar update views for other forms
@login_required
def form2_update(request, patient_id, form_id):
    """Update existing Form 2"""
    patient = get_object_or_404(Patient, id=patient_id)
    epworth = get_object_or_404(EpworthSleepinessScale, id=form_id, patient=patient)
    
    if request.method == 'POST':
        form = EpworthForm(request.POST, instance=epworth)
        if form.is_valid():
            form.save()
            messages.success(request, 'مقیاس خواب آلودگی با موفقیت بروزرسانی شد')
            return redirect('patient_detail', patient_id=patient.id)
    else:
        form = EpworthForm(instance=epworth)
    
    context = {
        'patient': patient,
        'form': form,
        'active_form': 'form2',
        'is_update': True,
    }
    return render(request, 'sleep_clinic/form2.html', context)


# AJAX Views for dynamic functionality
@login_required
def calculate_bmi(request):
    """AJAX endpoint to calculate BMI"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            height = float(data.get('height', 0))
            weight = float(data.get('weight', 0))
            
            if height > 0 and weight > 0:
                height_m = height / 100
                bmi = round(weight / (height_m ** 2), 2)
                return JsonResponse({'bmi': bmi})
            
            return JsonResponse({'error': 'Invalid input'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def patient_search_ajax(request):
    """AJAX endpoint for patient search autocomplete"""
    query = request.GET.get('q', '')
    if len(query) >= 2:
        patients = Patient.objects.filter(
            models.Q(first_name__icontains=query) |
            models.Q(last_name__icontains=query) |
            models.Q(patient_id__icontains=query)
        )[:10]
        
        results = [{
            'id': p.id,
            'text': f"{p.first_name} {p.last_name} - {p.patient_id}",
            'patient_id': p.patient_id,
        } for p in patients]
        
        return JsonResponse({'results': results})
    
    return JsonResponse({'results': []})


# Report Views
@login_required
def patient_report(request, patient_id):
    """Generate comprehensive patient report"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Get latest forms
    latest_info = patient.information_forms.first()
    latest_epworth = patient.epworth_forms.first()
    latest_medical = patient.medical_history_forms.first()
    latest_study = patient.sleep_study_results.first()
    
    context = {
        'patient': patient,
        'latest_info': latest_info,
        'latest_epworth': latest_epworth,
        'latest_medical': latest_medical,
        'latest_study': latest_study,
        'print_mode': True,
    }
    
    if request.GET.get('format') == 'pdf':
        # PDF generation logic here
        pass
    
    return render(request, 'sleep_clinic/patient_report.html', context)


@login_required
def epworth_trend(request, patient_id):
    """Show Epworth score trend over time"""
    patient = get_object_or_404(Patient, id=patient_id)
    epworth_scores = patient.epworth_forms.values('form_date', 'total_score').order_by('form_date')
    
    data = {
        'labels': [score['form_date'].strftime('%Y-%m-%d') for score in epworth_scores],
        'scores': [score['total_score'] for score in epworth_scores],
    }
    
    if request.is_ajax():
        return JsonResponse(data)
    
    context = {
        'patient': patient,
        'chart_data': json.dumps(data),
        'active_form': 'reports',
    }
    return render(request, 'sleep_clinic/epworth_trend.html', context)


# Class-based views for listing forms
@method_decorator(login_required, name='dispatch')
class PatientFormsListView(ListView):
    """List all forms for a specific patient"""
    template_name = 'sleep_clinic/patient_forms_list.html'
    context_object_name = 'forms'
    paginate_by = 10
    
    def get_queryset(self):
        self.patient = get_object_or_404(Patient, id=self.kwargs['patient_id'])
        form_type = self.kwargs.get('form_type', 'all')
        
        if form_type == 'epworth':
            return self.patient.epworth_forms.all()
        elif form_type == 'medical':
            return self.patient.medical_history_forms.all()
        # Add other form types as needed
        
        # Return all forms (custom implementation needed)
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = self.patient
        context['form_type'] = self.kwargs.get('form_type', 'all')
        context['active_form'] = 'patients'
        return context


# Utility function for form navigation
def get_next_form_url(current_form, patient_id):
    """Get the URL for the next form in sequence"""
    form_sequence = [
        ('form1', 'form2'),
        ('form2', 'form3'),
        ('form3', 'form4'),
        ('form4', 'form5'),
        ('form5', 'form6'),
        ('form6', 'form7'),
        ('form7', 'form8'),
        ('form8', 'patient_detail'),
    ]
    
    for current, next_form in form_sequence:
        if current == current_form:
            if next_form == 'patient_detail':
                return reverse_lazy('patient_detail', kwargs={'patient_id': patient_id})
            else:
                return reverse_lazy(f'{next_form}_create', kwargs={'patient_id': patient_id})
    
    return reverse_lazy('patient_detail', kwargs={'patient_id': patient_id})