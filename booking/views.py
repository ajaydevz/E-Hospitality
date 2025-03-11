from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DoctorSchedule, Appointment, Payment
from django.utils.timezone import now
import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import DoctorSchedule, Appointment, Payment, Notification
from accounts.models import DoctorProfile

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


@login_required(login_url='login')  # Redirect to login if user is not authenticated
def book_appointment(request, schedule_id):
    schedule = get_object_or_404(DoctorSchedule, id=schedule_id, is_booked=False)
    doctor_profile = get_object_or_404(DoctorProfile, user=schedule.doctor)

    stripe.api_key = settings.STRIPE_SECRET_KEY  # Ensure Stripe key is set

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('login')  # Redirect to login page

        # Create an appointment but don't confirm yet
        appointment = Appointment.objects.create(
            patient=request.user,  # Ensure user is logged in
            doctor_schedule=schedule,
            status="pending"
        )

        # Create Stripe Checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': f"Consultation with Dr. {schedule.doctor.first_name}"},
                    'unit_amount': int(doctor_profile.consultation_fee * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment_success', args=[appointment.id])),
            cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
        )

        return redirect(session.url)

    return redirect('doctor_detail', doctor_id=schedule.doctor.id)


def payment_success(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    schedule = appointment.doctor_schedule

    # Mark slot as booked
    schedule.is_booked = True
    schedule.save()

    # Create a payment entry
    Payment.objects.create(
        appointment=appointment,
        amount=appointment.doctor_schedule.doctor.doctor_profile.consultation_fee,
        status="paid"
    )

    # Send a notification to the doctor
    Notification.objects.create(
        doctor=appointment.doctor_schedule.doctor,
        message=f"New Appointment: {appointment.patient.first_name} booked on {appointment.doctor_schedule.date} at {appointment.doctor_schedule.start_time}."
    )

    # Confirm appointment
    appointment.status = "confirmed"
    appointment.save()

    return render(request, 'user/success.html', {'appointment': appointment})


def payment_cancel(request):
    return render(request, 'appointments/cancel.html')
