from django import forms
from .models import DoctorSchedule, Appointment
from django import forms
from .models import DoctorSchedule
from datetime import datetime, time

class DoctorScheduleForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedule
        fields = ['date', 'start_time', 'end_time']

    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')
        return self.convert_to_24_hour(start_time)

    def clean_end_time(self):
        end_time = self.cleaned_data.get('end_time')
        return self.convert_to_24_hour(end_time)

    def convert_to_24_hour(self, time_str):
        """
        Converts time from 12-hour format (e.g., "03:30 PM") to 24-hour format (e.g., "15:30:00").
        Handles cases where time is already a datetime.time object.
        """
        if isinstance(time_str, time):  
            return time_str  # If it's already a time object, return it as is
        
        if time_str:
            try:
                return datetime.strptime(time_str, "%I:%M %p").time()  # Converts to HH:MM:SS
            except ValueError:
                raise forms.ValidationError("Invalid time format. Please use AM/PM format.")
        return None

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = []
