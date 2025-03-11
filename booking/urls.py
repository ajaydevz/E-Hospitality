from django.urls import path
from . import views
from .views import book_appointment,payment_success,payment_cancel

urlpatterns = [
    path('doctor/set_schedule/', views.set_schedule, name='set_schedule'),
    

    path('book-appointment/<int:schedule_id>/', book_appointment, name="book_appointment"),

    path('payment-success/<int:appointment_id>/', payment_success, name="payment_success"),
    path('payment-cancel/', payment_cancel, name="payment_cancel"),
]
