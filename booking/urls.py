
from django.urls import path
from . import views

urlpatterns = [

    # Home
    path('', views.home_view, name='home'),

    # Authentication
    path('register/', views.register_view, name='register'),
    path(
    'lawyer-register/',
    views.lawyer_register_view,
    name='lawyer_register'
),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Lawyers
    path('lawyers/', views.lawyer_list_view, name='lawyer_list'),

    # Appointments
    path('book/', views.book_appointment_view, name='book_appointment'),

    path(
        'my-appointments/',
        views.my_appointments_view,
        name='my_appointments'
    ),

    # Lawyer dashboard
    path(
        'lawyer-dashboard/',
        views.lawyer_dashboard_view,
        name='lawyer_dashboard'
    ),

    # Approve or reject appointment
    path(
        'appointment/<int:appointment_id>/update-status/',
        views.update_appointment_status_view,
        name='update_appointment_status'
    ),

    # Cancel appointment
    path(
        'appointment/<int:appointment_id>/cancel/',
        views.cancel_appointment_view,
        name='cancel_appointment'
    ),
    
path(
    'payment/<int:appointment_id>/',
    views.create_payment_view,
    name='create_payment'
),

path(
    'payment/verify/<int:payment_id>/',
    views.verify_payment_view,
    name='verify_payment'
),
    

]
