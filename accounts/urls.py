from django.urls import path
from .views import index,Register,Login_view,AdminLoginView,AdminHome,admin_logout_view,add_doctor,admin_doctor_list,doctor_login,doctor_dashboard,doctor_logout,logout_view,doctor_list,doctor_details
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',index,name='home'),
    path('register/',Register,name='register'),
    path('login/',Login_view,name='login'),
    path('adminhome/',AdminHome,name='admin'),
    path('logout/',logout_view,name='logout'),
    path('doctor-list/',doctor_list,name='doctor-list'),
    path('doctor-detail/<int:doctor_id>/', doctor_details, name='doctor_details'),

    path('admin-login/', AdminLoginView, name='admin-login'),  # Admin Login
    path('admin-logout/', admin_logout_view, name='admin-logout'),
    path('doctor-list/', admin_doctor_list, name='doctors'),
    path('add-doctor/', add_doctor, name='add_doctor'),

    path('doctor-login/', doctor_login, name='doctor-login'),
    path('doctor-home/', doctor_dashboard, name='doctor-dashboard'),
    path('doctor-logout/', doctor_logout, name='doctor-logout'),



]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)