from django.urls import path
from . import views

urlpatterns = [
    path('doctor/set_schedule/', views.set_schedule, name='set_schedule'),
    path('book_appointment/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('payment/<int:appointment_id>/', views.payment_page, name='payment_page'),
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
]
