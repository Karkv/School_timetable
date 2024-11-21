from django.forms import modelformset_factory
from django.shortcuts import render,get_object_or_404, redirect
from .models import *
from .forms import *
from django.contrib import messages
from  .utils import *




# ________________________________________________________________________________________________----

def delete_class(request, class_id):
    school_class = get_object_or_404(Class, id=class_id)

    if request.method == 'POST':
        school_class.delete()
        messages.success(request, f"{school_class.name} deleted successfully!")
        return redirect('manage_classes')

    return render(request, 'admin_dashboard/confirm_delete_class.html', {
        'class': school_class,
    })
# __________________________________________________________________________________________________

# @login_required
def edit_class(request, class_id):
    school_class = get_object_or_404(Class, id=class_id)

    if request.method == 'POST':
        form = ClassForm(request.POST, instance=school_class)
        if form.is_valid():
            form.save()
            messages.success(request, f"{school_class.name} updated successfully!")
            return redirect('manage_classes')
    else:
        form = ClassForm(instance=school_class)

    return render(request, 'admin_dashboard/edit_class.html', {
        'form': form,
        'class': school_class,
    })
# _______________________________________________________________________________________________________
# @login_required
def delete_holiday(request, holiday_id):
    holiday = get_object_or_404(Holiday, id=holiday_id)
    if request.method == "POST":
        holiday.delete()
        messages.success(request, "Holiday deleted successfully!")
        return redirect("manage_holidays")

    return render(request, "admin_dashboard/confirm_delete_holiday.html", {"holiday": holiday})

# _____________________________________________________________________________________________________
def manage_holidays(request):
    """
    Displays and manages holidays for the current year.
    """
    # Fetch current year holidays from the holidays library
    current_year = datetime.now().year
    india_holidays = holidays.India(years=current_year)
    existing_holidays = Holiday.objects.all().order_by("date")

    # Add manually
    if request.method == "POST":
        form = HolidayForm(request.POST)
        if form.is_valid():
            holiday = form.save(commit=False)
            holiday.is_custom = True  # Mark as custom holiday
            holiday.save()
            messages.success(request, "Holiday added successfully!")
            return redirect("manage_holidays")
    else:
        form = HolidayForm()

    # Prepare context
    return render(request, "admin_dashboard/manage_holidays.html", {
        "form": form,
        "existing_holidays": existing_holidays,
        "india_holidays": india_holidays,
    })
# _________________________________________________________________________________________________________________________________

def admin_dashboard(request):
    # Fetch totals
    total_classes = Class.objects.count()
    total_subjects = Subject.objects.count()
    # total_teachers = Teacher.objects.count()  # If you have a Teacher model
    total_timetables = Timetable.objects.count()
    total_holidays = Holiday.objects.count()

    return render(request, 'admin_dashboard/admin_dashboard.html', {
        'total_classes': total_classes,
        'total_subjects': total_subjects,
        # 'total_teachers': total_teachers,
        'total_timetables': total_timetables,
        'total_holidays': total_holidays,
    })


# ___________________________________________________________________________________________________________________________--
def generate_timetable(request, class_id):
    """
    Generate a timetable temporarily and allow the user to save or discard it.
    """
    school_class = get_object_or_404(Class, id=class_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        # Save the timetable if user clicks "Save"
        if action == 'save':
            temporary_timetable = request.session.get('temporary_timetable', [])
            for entry in temporary_timetable:
                Timetable.objects.create(
                    class_assigned=school_class,
                    subject_id=entry['subject_id'],
                    date=entry['date'],
                    start_time=entry['start_time'],
                    end_time=entry['end_time'],
                    teacher_name=entry['teacher_name'],
                )
            request.session.pop('temporary_timetable', None)
            messages.success(request, "Timetable saved successfully!")
            return redirect('view_timetable', class_id=class_id)

        # Discard the timetable if user clicks "Cancel"
        elif action == 'cancel':
            request.session.pop('temporary_timetable', None)
            messages.info(request, "Timetable generation cancelled.")
            return redirect('manage_classes')

    # Generate the timetable temporarily
    temporary_timetable = generate_timetable_for_class(school_class)
    request.session['temporary_timetable'] = [
        {
            'subject_id': entry['subject'].id if entry['subject'] else None,
            'date': entry['date'].isoformat(),
            'start_time': entry['start_time'].isoformat(),
            'end_time': entry['end_time'].isoformat(),
            'teacher_name': entry['teacher_name'],
        }
        for entry in temporary_timetable
    ]

    return render(request, 'admin_dashboard/preview_timetables.html', {
        'class': school_class,
        'timetable': temporary_timetable,
    })


def view_timetable(request, class_id):
    """
    View the generated timetable for a class.
    """
    school_class = get_object_or_404(Class, id=class_id)
    timetables = Timetable.objects.filter(class_assigned=school_class).order_by('date', 'start_time')

    return render(request, 'admin_dashboard/view_timetable.html', {
        'class': school_class,
        'timetables': timetables,
    })


# _____________________________________________________________________________
def manage_classes(request):
    classes = Class.objects.all()  # Retrieve all classes
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Class added successfully!")
            return redirect('manage_classes')
    else:
        form = ClassForm()
    return render(request, 'admin_dashboard/manage_classes.html', {
        'classes': classes,
        'form': form
    })
# __________________________________________________________________________________________________________
def manage_subjects(request, class_id):
    """
    Handles the management of subjects for a specific class, including addition, editing, and deletion.
    """
    school_class = get_object_or_404(Class, id=class_id)

    # Create a formset for managing subjects
    SubjectFormSet = modelformset_factory(
        Subject,
        fields=('name', 'total_hours', 'teacher_name'),
        extra=1,  # Allow adding one extra row dynamically
        can_delete=True,  # Allow deletion of subjects
    )

    # Bind the formset with existing subjects for the selected class
    formset = SubjectFormSet(
        queryset=Subject.objects.filter(class_assigned=school_class),
        prefix='subjects',
    )

    if request.method == 'POST':
        formset = SubjectFormSet(
            request.POST,
            queryset=Subject.objects.filter(class_assigned=school_class),
            prefix='subjects',
        )
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data.get('DELETE'):
                    if form.instance.pk:
                        form.instance.delete()  # Delete existing subject
                else:
                    subject = form.save(commit=False)
                    subject.class_assigned = school_class
                    subject.save()
            messages.success(request, f"Subjects for {school_class.name} updated successfully!")
            return redirect('manage_subjects', class_id=class_id)

    return render(request, 'admin_dashboard/manage_subjects.html', {
        'formset': formset,
        'class': school_class,
    })


