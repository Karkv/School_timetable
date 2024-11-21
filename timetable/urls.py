from django.urls import path
from .import views

urlpatterns=[
    # path('',views.student_dashboard,name='student_dashboard'),
    path("manage-classes/", views.manage_classes, name="manage_classes"),
    path("class/<int:class_id>/manage-subjects/", views.manage_subjects, name="manage_subjects"),
    path("class/<int:class_id>/generate-timetable/", views.generate_timetable, name="generate_timetable"),
        path('class/<int:class_id>/view-timetable/', views.view_timetable, name='view_timetable'),

    path("manage-holidays/", views.manage_holidays, name="manage_holidays"),
    path("delete-holiday/<int:holiday_id>/", views.delete_holiday, name="delete_holiday"),
    path('manage-classes/', views.manage_classes, name='manage_classes'),
    path('edit-class/<int:class_id>/', views.edit_class, name='edit_class'),
    path('delete-class/<int:class_id>/', views.delete_class, name='delete_class'),
    path("",views.admin_dashboard,name='admin_dashboard'),

]