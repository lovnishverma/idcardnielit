# myapp/urls.py
from django.urls import path
from .views import (
    employee_list,
    student_list,
    employee_detail,
    generate_qr,
    download_id_card,
    register,
    student_detail,
    download_employee_card,
    download_student_card,
    create_course,
    create_branch,
    get_branches
)

urlpatterns = [
    path('', register, name='add_employee'),
    path('api/get_branches/', get_branches, name='get_branches'),
    path('list/', employee_list, name='employee_list'),
    path('students/', student_list, name='student_list'),
    path('employee/<str:employee_id>/', employee_detail, name='employee_detail'),
    path('employee/<str:employee_id>/download/', download_employee_card, name='download_employee_card'),
    path('student_detail/<str:enrollment_number>/', student_detail, name='student_detail'),
    path('student_detail/<str:enrollment_number>/download/', download_student_card, name='download_student_card'),
    path('student/<str:enrollment_number>/download/', download_student_card, name='download_student_card_alt'),
    path('generate_qr/<str:employee_id>/', generate_qr, name='generate_qr'),
    path('list/download/', download_id_card, name='download_id_card'),
    path('create_course/', create_course, name='create_course'),
    path('create_branch/', create_branch, name='create_branch'),
    path('<str:employee_id>/', employee_detail, name='employee_detail_legacy'),
]
