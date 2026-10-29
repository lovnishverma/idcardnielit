# myapp/views.py
from django.shortcuts import render, get_object_or_404
from .models import Employee

def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'myapp/employee_list.html', {'employees': employees})

def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)
    return render(request, 'myapp/employee_detail.html', {'employee': employee})
