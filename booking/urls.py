from django.urls import path
from . import views
from .views import book_appointment,payment_success,payment_cancel,doctor_notifications,delete_schedule

urlpatterns = [
    path('doctor/set_schedule/', views.set_schedule, name='set_schedule'),
    path('delete-schedule/<int:schedule_id>/', delete_schedule, name='delete_schedule'),
    

    path('book-appointment/<int:schedule_id>/', book_appointment, name="book_appointment"),

    path('payment-success/<int:appointment_id>/', payment_success, name="payment_success"),
    path('payment-cancel/', payment_cancel, name="payment_cancel"),

    path("doctor/notifications/", doctor_notifications, name="doctor_notifications"),
]
