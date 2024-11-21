from django import forms
from .models import Class, Subject,Holiday

# class ClassForm(forms.ModelForm):
#     class Meta:
#         model = Class
#         fields = ['name', 'start_date', 'start_time', 'end_time',]  # Exclude lunch fields
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["name", "teacher_name", "total_hours"]


class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = ["name", "date"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'start_date', 'start_time', 'end_time', 'lunch_start', 'lunch_end' ,'period_duration']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'lunch_start': forms.TimeInput(attrs={'type': 'time'}),
            'lunch_end': forms.TimeInput(attrs={'type': 'time'}),
        }
