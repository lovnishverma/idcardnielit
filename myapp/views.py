import os
import zipfile
from io import BytesIO
import qrcode
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.conf import settings

from .forms import EmployeeForm, StudentForm, CourseForm, BranchForm
from .models import Employee, Student, Department, Branch, Course
from .Card.GenerateCard import (
    write_front_text,
    write_text_back,
    write_front_image,
    write_qr,
    write_front_text_student,
    write_text_back_student,
    write_qr_student
)
from .Card.pdf_generator import (
    generate_cr80_pdf,
    generate_a4_single_card_pdf,
    generate_bulk_a4_pdf
)
from .Card.docx_generator import generate_cards_docx


def employee_list(request):
    query = request.GET.get('q', '').strip()
    dept_id = request.GET.get('department', '').strip()

    qs = Employee.objects.select_related('department').all()
    if query:
        qs = qs.filter(name__icontains=query) | qs.filter(employee_id__icontains=query) | qs.filter(job_title__icontains=query)
    if dept_id:
        qs = qs.filter(department_id=dept_id)

    departments = Department.objects.all()
    return render(request, 'employee_list.html', {
        'employees': qs,
        'departments': departments,
        'selected_dept': dept_id,
        'query': query,
    })


def student_list(request):
    query = request.GET.get('q', '').strip()
    course_id = request.GET.get('course', '').strip()

    qs = Student.objects.select_related('course', 'branch').all()
    if query:
        qs = qs.filter(name__icontains=query) | qs.filter(enrollment_number__icontains=query) | qs.filter(batch__icontains=query)
    if course_id:
        qs = qs.filter(course_id=course_id)

    courses = Course.objects.all()
    return render(request, 'student_list.html', {
        'students': qs,
        'courses': courses,
        'selected_course': course_id,
        'query': query,
    })


def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee.objects.select_related('department'), employee_id=employee_id)
    static_dir = os.path.join(settings.BASE_DIR, 'static', 'download')
    front_path = os.path.join(static_dir, f'{employee.employee_id}_front.jpg')
    back_path = os.path.join(static_dir, f'{employee.employee_id}_back.jpg')

    # Ensure cards are pre-generated
    if not (os.path.exists(front_path) and os.path.exists(back_path)):
        try:
            generate_qr(None, request, [employee])
        except Exception as e:
            print(f"Auto-generate card failed for {employee_id}: {e}")

    has_card = os.path.exists(front_path) and os.path.exists(back_path)
    return render(request, 'employee_detail.html', {
        'employee': employee,
        'has_card': has_card,
        'front_card_url': f'/static/download/{employee.employee_id}_front.jpg',
        'back_card_url': f'/static/download/{employee.employee_id}_back.jpg',
    })


def student_detail(request, enrollment_number):
    student = get_object_or_404(Student.objects.select_related('course', 'branch'), enrollment_number=enrollment_number)
    static_dir = os.path.join(settings.BASE_DIR, 'static', 'download')
    front_path = os.path.join(static_dir, f'{student.enrollment_number}_front.jpg')
    back_path = os.path.join(static_dir, f'{student.enrollment_number}_back.jpg')

    # Ensure cards are pre-generated
    if not (os.path.exists(front_path) and os.path.exists(back_path)):
        try:
            generate_student(None, request, [student])
        except Exception as e:
            print(f"Auto-generate student card failed for {enrollment_number}: {e}")

    has_card = os.path.exists(front_path) and os.path.exists(back_path)
    return render(request, 'student_detail.html', {
        'student': student,
        'has_card': has_card,
        'front_card_url': f'/static/download/{student.enrollment_number}_front.jpg',
        'back_card_url': f'/static/download/{student.enrollment_number}_back.jpg',
    })


def register(request):
    employee_form = EmployeeForm()
    student_form = StudentForm()

    if request.method == 'POST':
        if 'employee_submit' in request.POST:
            employee_form = EmployeeForm(request.POST, request.FILES)
            if employee_form.is_valid():
                emp = employee_form.save()
                try:
                    generate_qr(None, request, [emp])
                except Exception as e:
                    print(f"Error auto-generating card for {emp.employee_id}: {e}")
                messages.success(request, f'Registration successful for {emp.name}. ID Card generated.')
                return redirect('employee_detail', employee_id=emp.employee_id)
            else:
                messages.error(request, 'Employee registration failed. Please check form errors below.')
        elif 'student_submit' in request.POST:
            student_form = StudentForm(request.POST, request.FILES)
            if student_form.is_valid():
                stu = student_form.save()
                try:
                    generate_student(None, request, [stu])
                except Exception as e:
                    print(f"Error auto-generating card for {stu.enrollment_number}: {e}")
                messages.success(request, f'Registration successful for {stu.name}. ID Card generated.')
                return redirect('student_detail', enrollment_number=stu.enrollment_number)
            else:
                messages.error(request, 'Student registration failed. Please check form errors below.')

    return render(request, 'register.html', {'employee_form': employee_form, 'student_form': student_form})


def get_branches(request):
    course_id = request.GET.get('course_id')
    if course_id:
        branches = Branch.objects.filter(course_id=course_id).values('id', 'branch_name')
        return JsonResponse(list(branches), safe=False)
    return JsonResponse([], safe=False)


def generate_qr(request_or_admin, request=None, queryset=None, employee_id=None):
    if employee_id:
        req = request_or_admin
        emp = get_object_or_404(Employee, employee_id=employee_id)
        qs = [emp]
    else:
        req = request if request is not None else (request_or_admin if hasattr(request_or_admin, 'build_absolute_uri') else None)
        qs = queryset if queryset is not None else []

    card_dir = os.path.join(settings.BASE_DIR, 'myapp', 'Card')
    qr_code_directory = os.path.join(settings.BASE_DIR, 'static', 'QR')
    os.makedirs(qr_code_directory, exist_ok=True)

    for emp in qs:
        try:
            dept = emp.department

            # Determine front and back template paths from Department model
            front_template_path = None
            back_template_path = None

            if dept and dept.front_template:
                front_template_path = dept.front_template.path
            if dept and dept.back_template:
                back_template_path = dept.back_template.path

            base_template_code = dept.template_code if dept and dept.template_code else 'FACULTY_TEMPLATE'

            if not front_template_path:
                front_template_path = os.path.join(card_dir, f"{base_template_code}_FRONT.png")
            if not back_template_path:
                back_template_path = os.path.join(card_dir, f"{base_template_code}_BACK.png")

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            url = req.build_absolute_uri(f'/employee/{emp.employee_id}/') if req else f'/employee/{emp.employee_id}/'
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            img_path = os.path.join(qr_code_directory, f"{emp.employee_id}.png")
            img.save(img_path)

            name = emp.name
            emp_id = emp.employee_id
            email = emp.email or ""
            phone = emp.contact or ""
            jdate = emp.join_date
            edate = emp.end_date
            dept_name = dept.name if dept else ""

            image_bytes = None
            if emp.profile_image:
                try:
                    if hasattr(emp.profile_image, 'path') and os.path.exists(emp.profile_image.path):
                        with open(emp.profile_image.path, 'rb') as f:
                            image_bytes = f.read()
                    else:
                        emp.profile_image.open('rb')
                        image_bytes = emp.profile_image.read()
                except Exception as e:
                    print(f"Error reading image for {emp_id}: {e}")

            write_front_text(name, emp_id, email, phone, front_template_path)
            write_text_back(dept_name, jdate, edate, back_template_path, emp_id)
            write_front_image(image_bytes, emp_id)
            write_qr(img_path, emp_id)

        except Employee.DoesNotExist:
            return JsonResponse({"message": "Employee not found."}, status=404)

    return JsonResponse({"message": "ID Cards generated successfully."})


def generate_student(modeladmin, request, queryset):
    card_dir = os.path.join(settings.BASE_DIR, 'myapp', 'Card')
    qr_code_directory = os.path.join(settings.BASE_DIR, 'static', 'QR')
    os.makedirs(qr_code_directory, exist_ok=True)

    front_template_path = os.path.join(card_dir, "STUDENT_TEMPLATE_FRONT.png")
    back_template_path = os.path.join(card_dir, "STUDENT_TEMPLATE_BACK.png")

    for stu in queryset:
        try:
            stu = Student.objects.select_related('course', 'branch').get(enrollment_number=stu.enrollment_number)

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            url = request.build_absolute_uri(f'/student_detail/{stu.enrollment_number}/') if request else f'/student_detail/{stu.enrollment_number}/'
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            qr_img_path = os.path.join(qr_code_directory, f"{stu.enrollment_number}.png")
            img.save(qr_img_path)

            enrollment_number = stu.enrollment_number
            name = stu.name
            course = stu.course.course_name if stu.course else ""
            branch = stu.branch.branch_name if stu.branch else ""
            phone = stu.contact or ""
            batch = stu.batch
            valid_date_from = stu.valid_date_from
            date_upto = stu.date_upto

            image_bytes = None
            if stu.profile_image:
                try:
                    if hasattr(stu.profile_image, 'path') and os.path.exists(stu.profile_image.path):
                        with open(stu.profile_image.path, 'rb') as f:
                            image_bytes = f.read()
                    else:
                        stu.profile_image.open('rb')
                        image_bytes = stu.profile_image.read()
                except Exception as e:
                    print(f"Error reading student image for {enrollment_number}: {e}")

            address1 = f"{stu.city or ''} {stu.district or ''}".strip()
            address2 = f"{stu.state or ''} {stu.pincode or ''}".strip()

            write_front_text_student(name, enrollment_number, course, branch, phone, front_template_path)
            write_text_back_student(batch, valid_date_from, date_upto, address1, address2, back_template_path, enrollment_number)
            write_front_image(image_bytes, enrollment_number)
            write_qr_student(qr_img_path, enrollment_number)

        except Student.DoesNotExist:
            return JsonResponse({"message": "Student not found."}, status=404)

    return JsonResponse({"message": "Student cards generated successfully."})


def download_employee_card(request, employee_id):
    employee = get_object_or_404(Employee.objects.select_related('department'), employee_id=employee_id)
    # Generate/refresh cards
    generate_qr(None, request, [employee])

    static_dir = os.path.join(settings.BASE_DIR, 'static', 'download')
    front_path = os.path.join(static_dir, f'{employee.employee_id}_front.jpg')
    back_path = os.path.join(static_dir, f'{employee.employee_id}_back.jpg')

    fmt = request.GET.get('format', 'pdf').lower()

    if fmt == 'cr80':
        buf = BytesIO()
        generate_cr80_pdf(front_path, back_path, buf)
        response = HttpResponse(buf.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{employee.employee_id}_cr80_card.pdf"'
        return response
    elif fmt == 'docx':
        buf = BytesIO()
        try:
            generate_cards_docx([{'front': front_path, 'back': back_path, 'title': f"{employee.name} ({employee.employee_id})"}], buf, back_first=True)
        except ImportError as e:
            return HttpResponse(f"Word export is not available: {e}", status=500)
        response = HttpResponse(buf.getvalue(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="{employee.employee_id}_idcard.docx"'
        return response
    elif fmt == 'pdf':
        buf = BytesIO()
        dept_str = f" - {employee.department.name}" if employee.department else ""
        generate_a4_single_card_pdf(front_path, back_path, f"{employee.name} ({employee.employee_id}){dept_str}", buf)
        response = HttpResponse(buf.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{employee.employee_id}_idcard.pdf"'
        return response
    else:
        # ZIP archive
        buf = BytesIO()
        with zipfile.ZipFile(buf, 'w') as zipf:
            if os.path.exists(front_path):
                zipf.write(front_path, f'{employee.employee_id}_front.jpg')
            if os.path.exists(back_path):
                zipf.write(back_path, f'{employee.employee_id}_back.jpg')
        response = HttpResponse(buf.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{employee.employee_id}_card_images.zip"'
        return response


def download_student_card(request, enrollment_number):
    student = get_object_or_404(Student.objects.select_related('course', 'branch'), enrollment_number=enrollment_number)
    # Generate/refresh cards
    generate_student(None, request, [student])

    static_dir = os.path.join(settings.BASE_DIR, 'static', 'download')
    front_path = os.path.join(static_dir, f'{student.enrollment_number}_front.jpg')
    back_path = os.path.join(static_dir, f'{student.enrollment_number}_back.jpg')

    fmt = request.GET.get('format', 'pdf').lower()

    if fmt == 'cr80':
        buf = BytesIO()
        generate_cr80_pdf(front_path, back_path, buf)
        response = HttpResponse(buf.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{student.enrollment_number}_cr80_card.pdf"'
        return response
    elif fmt == 'docx':
        buf = BytesIO()
        try:
            generate_cards_docx([{'front': front_path, 'back': back_path, 'title': f"{student.name} ({student.enrollment_number})"}], buf, back_first=True)
        except ImportError as e:
            return HttpResponse(f"Word export is not available: {e}", status=500)
        response = HttpResponse(buf.getvalue(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="{student.enrollment_number}_idcard.docx"'
        return response
    elif fmt == 'pdf':
        buf = BytesIO()
        course_str = f" - {student.course.course_name}" if student.course else ""
        generate_a4_single_card_pdf(front_path, back_path, f"{student.name} ({student.enrollment_number}){course_str}", buf)
        response = HttpResponse(buf.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{student.enrollment_number}_idcard.pdf"'
        return response
    else:
        # ZIP archive
        buf = BytesIO()
        with zipfile.ZipFile(buf, 'w') as zipf:
            if os.path.exists(front_path):
                zipf.write(front_path, f'{student.enrollment_number}_front.jpg')
            if os.path.exists(back_path):
                zipf.write(back_path, f'{student.enrollment_number}_back.jpg')
        response = HttpResponse(buf.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{student.enrollment_number}_card_images.zip"'
        return response


def download_id_card(request):
    download_dir = os.path.join(settings.BASE_DIR, 'static', 'download')
    file_paths = [
        os.path.join(download_dir, 'idcard_front.jpg'),
        os.path.join(download_dir, 'idcard_back.jpg')
    ]
    zip_file_name = "wbl-card.zip"

    if all(os.path.exists(path) for path in file_paths):
        in_memory_zip = BytesIO()
        with zipfile.ZipFile(in_memory_zip, 'w') as zipf:
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                zipf.write(file_path, file_name)

        response = HttpResponse(in_memory_zip.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{zip_file_name}"'
        return response
    else:
        return HttpResponse("Files not found! Make sure ID cards are generated first.")


def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = CourseForm()

    return render(request, 'create_course.html', {'form': form})


def create_branch(request):
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = BranchForm()

    return render(request, 'create_branch.html', {'form': form})
