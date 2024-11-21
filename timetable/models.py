
from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

class Class(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    lunch_start = models.TimeField(null=True, blank=True)
    lunch_end = models.TimeField(null=True, blank=True)

    
    period_duration = models.IntegerField(
        help_text="Duration of each period in minutes",
        default=45
    )

    def __str__(self):
        return self.name

# Subject Model
class Subject(models.Model):
    name = models.CharField(max_length=100, help_text="Subject name")
    teacher_name = models.CharField(max_length=100, help_text="Teacher assigned to the subject")
    total_hours = models.PositiveIntegerField(help_text="Total hours for the subject per year")
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="subjects")

    def __str__(self):
        return f"{self.name} - {self.teacher_name} ({self.class_assigned.name})"

# Timetable Model
class Timetable(models.Model):
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="timetables")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="timetables", null=True, blank=True)
    date = models.DateField(help_text="Date of the timetable entry")
    start_time = models.TimeField(help_text="Start time of the period")
    end_time = models.TimeField(help_text="End time of the period")
    teacher_name = models.CharField(max_length=100, help_text="Teacher assigned for this period", null=True, blank=True)

    def __str__(self):
        return f"{self.subject.name if self.subject else 'Lunch Break'} ({self.class_assigned.name}) on {self.date}"

# Holiday Model
class Holiday(models.Model):
    name = models.CharField(max_length=100, help_text="Holiday name")
    date = models.DateField(unique=True, help_text="Date of the holiday")
    is_custom = models.BooleanField(default=False, help_text="Is this a manually added holiday?")

    def __str__(self):
        return f"{self.name} ({self.date})"