from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DoctorSchedule, Appointment, Payment
from django.utils.timezone import now

# Doctor: Set Schedule (Traditional Form)
@login_required
def set_schedule(request):
    if request.user.role != 'doctor':
        messages.error(request, "You are not authorized!")
        return redirect('home')

    if request.method == 'POST':
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        DoctorSchedule.objects.create(doctor=request.user, date=date, start_time=start_time, end_time=end_time)
        messages.success(request, "Schedule added successfully!")
        return redirect('set_schedule')

    schedules = DoctorSchedule.objects.filter(doctor=request.user)
    return render(request, 'doctor/set_schedule.html', {'schedules': schedules})

# User: View Doctor Schedules and Book
@login_required
def book_appointment(request, doctor_id):
    schedules = DoctorSchedule.objects.filter(doctor_id=doctor_id, is_booked=False)

    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        schedule = get_object_or_404(DoctorSchedule, id=schedule_id)
        schedule.is_booked = True
        schedule.save()

        appointment = Appointment.objects.create(patient=request.user, doctor_schedule=schedule)
        Payment.objects.create(appointment=appointment, amount=50.00, status='pending')

        messages.success(request, "Appointment booked! Please proceed with payment.")
        return redirect('payment_page', appointment_id=appointment.id)

    return render(request, 'patient/book_appointment.html', {'schedules': schedules})

# Payment Page
@login_required
def payment_page(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        appointment.payment.status = 'paid'
        appointment.payment.save()
        messages.success(request, "Payment successful!")
        return redirect('patient_dashboard')

    return render(request, 'payment/payment_page.html', {'appointment': appointment})

# Doctor: View Appointments
@login_required
def doctor_appointments(request):
    if request.user.role != 'doctor':
        messages.error(request, "Unauthorized access!")
        return redirect('home')

    appointments = Appointment.objects.filter(doctor_schedule__doctor=request.user)
    return render(request, 'doctor/appointments.html', {'appointments': appointments})
