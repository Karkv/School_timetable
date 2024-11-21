from datetime import timedelta, datetime
from .models import Timetable, Holiday
import holidays

from django.db.models import Q


def fetch_and_save_indian_holidays(year=None):
    """
    Fetch Indian holidays for the given year using the `holidays` library and save them to the database.
    If no year is provided, fetch holidays for the current year.
    """
    year = year or datetime.now().year  # Use the current year if no year is specified
    indian_holidays = holidays.India(years=year)
    for date, name in indian_holidays.items():
        Holiday.objects.get_or_create(name=name, date=date, is_custom=False)


def generate_timetable_for_class(school_class):
    """
    Generate a timetable for a specific class and its subjects sequentially, including a lunch break.
    """
    current_date = school_class.start_date
    end_time = datetime.combine(datetime.today(), school_class.end_time)
    start_time = datetime.combine(datetime.today(), school_class.start_time)
    lunch_start = school_class.lunch_start
    lunch_end = school_class.lunch_end
    period_duration = timedelta(minutes=school_class.period_duration)
    daily_duration = (end_time - start_time).seconds // 60  # Total daily duration in minutes

    holidays = set(Holiday.objects.values_list('date', flat=True))

    subjects = school_class.subjects.all()  # Fetch all subjects assigned to the class
    subject_durations = {subject.id: subject.total_hours * 60 for subject in subjects}  # Convert hours to minutes
    timetable=[]
    while any(duration > 0 for duration in subject_durations.values()):
        period_start_time = start_time.time()

        for subject in subjects:
            if subject_durations[subject.id] <= 0:
                continue

            # If it's lunch time, include a lunch break in the timetable
            if lunch_start and lunch_end and lunch_start <= period_start_time < lunch_end:
                timetable.append({
                    'class_assigned': school_class,
                    'subject': None,  # No subject for lunch
                    'date': current_date,
                    'start_time': lunch_start,
                    'end_time': lunch_end,
                    'teacher_name': "Lunch Break",
                })
                period_start_time = lunch_end  # Resume scheduling after lunch
                continue
            # Calculate the period end time
            period_end_time = (datetime.combine(datetime.today(), period_start_time) + period_duration).time()

            # If there's not enough time left in the day, move to the next day
            if datetime.combine(current_date, period_end_time) > datetime.combine(current_date, school_class.end_time):
                break

            # Skip holidays and weekends
            if current_date.weekday() in [5, 6] or current_date in holidays:
                current_date += timedelta(days=1)
                period_start_time = start_time.time()
                continue

            # Add the subject to the temporary timetable
            timetable.append({
                'class_assigned': school_class,
                'subject': subject,
                'date': current_date,
                'start_time': period_start_time,
                'end_time': period_end_time,
                'teacher_name': subject.teacher_name,
            })

            # Deduct the scheduled time
            subject_durations[subject.id] -= period_duration.seconds // 60
            period_start_time = period_end_time

        # Move to the next day after all subjects are scheduled for the day
        current_date += timedelta(days=1)

    return timetable




def is_time_slot_free(class_assigned, date, start_time, end_time):
    return not Timetable.objects.filter(
        class_assigned=class_assigned,
        date=date,
        start_time__lt=end_time,
        end_time__gt=start_time,
    ).exists()

