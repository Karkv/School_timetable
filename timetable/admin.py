from django.contrib import admin
from .models import Class, Subject, Timetable, Holiday

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'start_time', 'end_time', 'period_duration')  # Include method
    search_fields = ("name",)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "teacher_name", "total_hours", "class_assigned")
    search_fields = ("name", "teacher_name")

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ("class_assigned", "subject", "date", "start_time", "end_time", "teacher_name")
    search_fields = ("class_assigned__name", "subject__name", "teacher_name")

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ("name", "date")
    search_fields = ("name",)
