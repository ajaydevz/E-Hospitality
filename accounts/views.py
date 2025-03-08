from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from .models import CustomUser,DoctorProfile
from booking.models import DoctorSchedule
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required, user_passes_test
import random
import string
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.core.mail import send_mail

@never_cache
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def index(request):
    doctors = DoctorProfile.objects.all()
    return render(request, 'user/index.html',{'doctors':doctors})


def Register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role', 'patient')

        print(f"Registration attempt with email: {email}")

        if not all([email, first_name, last_name, phone_number, password]):
            messages.error(request, "All fields are required.")
            return redirect('register')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        # create user with hashed password
        try:
            user = CustomUser.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                password=password,
                role=role
            )
            print(f"User created successfully: {user.email}, User ID: {user.id}")
            
            # Verify user exists in database
            check_user = CustomUser.objects.get(email=email)
            print(f"Verified user in database: {check_user.email}, ID: {check_user.id}")
            
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            messages.error(request, f"Registration failed: {str(e)}")
            return redirect('register')

    return render(request, 'user/Register.html')


def Login_view(request):
    print('Entering login...')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)  # Now supports email login
        print('User >>>>>>>>', user)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            
            if user.is_superuser:
                return redirect('admin')  # Redirect superuser to dashboard
            return redirect('home')  # Redirect normal users to home
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login')

    return render(request, 'user/Login.html')

@login_required
def logout_view(request):
    logout(request)  
    messages.success(request, "You have been logged out.")
    return redirect('login')  # Redirect to login page


# Adminside >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

@cache_control(no_store=True, no_cache=True, must_revalidate=True)
@login_required(login_url='admin-login')
def AdminHome(request):
    if not request.user.is_superuser:
        messages.error(request,'unauthorised acess!!')
        return redirect('admin-login')
    return render(request,'adminhome/dashboard.html')


@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def AdminLoginView(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin')  
     
    print('heyyyyy')
    if request.method == 'POST':
        email = request.POST.get('email')  # Fix 
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Both email and password are required.")
            return redirect('admin-login')

        
        user = authenticate(request, email=email, password=password)  # Pass email instead of username
        print('username>>>>>>>>>>>>>>>>>>>>>',user)

        if user is not None and user.is_superuser:
            login(request, user)
            print('succesfully admin login<<<<<<<<<<<<<<<<<<')
            messages.success(request, "Admin login successful!")
            return redirect('admin')  # Redirect to admin dashboard
        else:
            messages.error(request, "Invalid admin credentials.")
            return redirect('admin-login')

    return render(request, 'adminhome/sign-in.html')

@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def admin_logout_view(request):
    logout(request)
    response = redirect('admin-login')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    messages.success(request, "Admin logged out successfully.")
    return response


def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def admin_doctor_list(request):
    doctors = DoctorProfile.objects.all()
    return render(request, 'adminhome/tables.html', {'doctors': doctors})



def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


@login_required
@user_passes_test(is_admin)
@cache_control(no_store=True, no_cache=True, must_revalidate=True)
def add_doctor(request):
    print("DATA RECEIVED >>>", request.POST, request.FILES)    

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')


        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Doctor with this email already exists!'}, status=400)


        password = generate_password()

        doctor = CustomUser.objects.create_user(
            email=email,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            phone_number=request.POST.get('phone_number'),
            password=password,
            role='doctor',
            is_staff=True
        )

        image = request.FILES.get('image', 'doctor_images/default.jpg')

        DoctorProfile.objects.create(
            user=doctor,
            specialization=request.POST.get('specialization'),
            qualification=request.POST.get('qualification'),
            experience=request.POST.get('experience'),
            bio=request.POST.get('bio'),
            image=image 
        )

        send_mail(
            'Doctor Account Created',
            f'Hello Dr. {first_name},\n\nYour account has been created.\nEmail: {email}\nPassword: {password}\n\nPlease login and work with us!.',
            'admin@medicohospital.com',
            [email],
            fail_silently=False,
        )
        

        return JsonResponse({"success": "Doctor added successfully!"})
        
    return JsonResponse({"error": "Invalid request"}, status=400)


@never_cache
def doctor_login(request):
    if request.user.is_authenticated and request.user.role == "doctor":
        return redirect("doctor-dashboard")  # Redirect if already logged in
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        doctor = authenticate(request, username=email, password=password)

        if doctor is not None and doctor.role == "doctor":
            login(request, doctor)
            request.session["doctor_id"] = doctor.id  # Store doctor ID in session
            request.session.set_expiry(1800)  # Auto logout after 30 minutes
            messages.success(request, "Login successful!")
            return redirect("doctor-dashboard")
        else:
            return render(request, "doctor/doctor-login.html", {"error": "Invalid credentials!"})

    return render(request, "doctor/doctor-login.html")


@login_required(login_url="doctor-login")  
@never_cache  # Prevents the browser from caching the page
def doctor_dashboard(request):
    if request.user.role != "doctor":
        messages.error(request, "Unauthorized access!")
        return redirect("doctor-login")
    
    try:
        doctor = DoctorProfile.objects.get(user=request.user)
    except DoctorProfile.DoesNotExist:
        messages.error(request, "Doctor profile not found!")
        return redirect("doctor-login")

    context = {
        "doctor": doctor,  #
    }

    return render(request, "doctor/doctor_dashboard.html",context)


@login_required(login_url="doctor-login") 
def doctor_logout(request):
    request.session.flush()  # Clear all session data
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("doctor-login")


def doctor_list(request):
    doctors = DoctorProfile.objects.all()
    return render(request,'user/doctor.html',{'doctors':doctors})


def doctor_details(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    schedules = DoctorSchedule.objects.filter(doctor=doctor.user)

    context ={
        'doctor':doctor,
        'schedules':schedules
    }
    return render(request, 'user/doctor_detail.html', context)