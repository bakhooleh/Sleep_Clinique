from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from patient_app import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', include('login_app.urls')),
    path('', include('patient_app.urls')),

    # Dashboard and main pages
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Patient management
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:patient_id>/report/', views.patient_report, name='patient_report'),
    path('patients/<int:patient_id>/epworth-trend/', views.epworth_trend, name='epworth_trend'),
    path('patients/<int:patient_id>/forms/<str:form_type>/', 
         views.PatientFormsListView.as_view(), name='patient_forms_list'),
    
    # Form 1 - Patient Information
    path('form1/', views.form1_create, name='form1'),
    path('form1/<int:patient_id>/', views.form1_create, name='form1_create'),
    path('form1/<int:patient_id>/update/<int:form_id>/', views.form1_update, name='form1_update'),
    
    # Form 2 - Epworth Sleepiness Scale
    path('form2/', views.form2_create, name='form2'),
    path('form2/<int:patient_id>/', views.form2_create, name='form2_create'),
    path('form2/<int:patient_id>/update/<int:form_id>/', views.form2_update, name='form2_update'),
    
    # Form 3 - Medical History
    path('form3/', views.form3_create, name='form3'),
    path('form3/<int:patient_id>/', views.form3_create, name='form3_create'),
    
    # Form 4 - Physical Examination
    path('form4/', views.form4_create, name='form4'),
    path('form4/<int:patient_id>/', views.form4_create, name='form4_create'),
    
    # Form 5 - Daily Symptom Assessment
    path('form5/', views.form5_create, name='form5'),
    path('form5/<int:patient_id>/', views.form5_create, name='form5_create'),
    
    # Form 6 - Clinical Examination Details
    path('form6/', views.form6_create, name='form6'),
    path('form6/<int:patient_id>/', views.form6_create, name='form6_create'),
    
    # Form 7 - PAP Titration
    path('form7/', views.form7_create, name='form7'),
    path('form7/<int:patient_id>/', views.form7_create, name='form7_create'),
    
    # Form 8 - Supplementary Information
    path('form8/', views.form8_create, name='form8'),
    path('form8/<int:patient_id>/', views.form8_create, name='form8_create'),
    
    # AJAX endpoints
    path('ajax/calculate-bmi/', views.calculate_bmi, name='calculate_bmi'),
    path('ajax/patient-search/', views.patient_search_ajax, name='patient_search_ajax'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)