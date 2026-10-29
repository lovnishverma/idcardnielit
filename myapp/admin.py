# myapp/admin.py
import os
import zipfile
from io import BytesIO
import csv
import pandas as pd

from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils.html import format_html

from .models import Employee, Student, Course, Branch, Department
from .views import generate_qr, generate_student
from .Card.pdf_generator import (
    generate_cr80_pdf,
    generate_a4_single_card_pdf,
    generate_bulk_a4_pdf
)
from .Card.docx_generator import generate_cards_docx


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_code', 'has_custom_front', 'has_custom_back', 'employee_count']
    search_fields = ['name']
    list_filter = ['template_code']

    def has_custom_front(self, obj):
        return bool(obj.front_template)
    has_custom_front.boolean = True
    has_custom_front.short_description = "Custom Front PNG"

    def has_custom_back(self, obj):
        return bool(obj.back_template)
    has_custom_back.boolean = True
    has_custom_back.short_description = "Custom Back PNG"

    def employee_count(self, obj):
        return obj.employees.count()
    employee_count.short_description = "Employees"


class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'employee_id', 'department', 'dob', 'gender',
        'contact', 'email', 'job_title', 'join_date', 'end_date',
        'work_location', 'display_image'
    ]
    search_fields = ['name', 'employee_id', 'job_title', 'department__name']
    list_filter = ['department', 'job_title', 'join_date', 'end_date', 'gender']
    ordering = ['name', 'employee_id', 'join_date', 'end_date']

    def display_image(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="45" height="45" style="border-radius: 50%; object-fit: cover;">', obj.profile_image.url)
        return "-"

    display_image.short_description = 'Photo'

    actions = [
        'export_to_docx_action',
        'download_pdf_a4_action',
        'download_pdf_cr80_action',
        'download_id_card_action',
        'generate_qr_action',
        'export_to_excel_csv'
    ]

    def export_to_docx_action(self, request, queryset):
        generate_qr(self, request, queryset)
        static_dir = os.path.join(settings.BASE_DIR, 'static', 'download')

        pairs = []
        for obj in queryset:
            front = os.path.join(static_dir, f'{obj.employee_id}_front.jpg')
            back = os.path.join(static_dir, f'{obj.employee_id}_back.jpg')
            if os.path.exists(front) and os.path.exists(back):
                pairs.append({
                    'front': front,
                    'back': back,
                    'title': f"{obj.name} ({obj.employee_id})"
                })

        if not pairs:
            self.message_user(request, "Could not generate cards for Word export.", level=messages.ERROR)
            return None

        buf = BytesIO()
        try:
            generate_cards_docx(pairs, buf, back_first=True)
        except ImportError as e:
            self.message_user(request, f"Word export error: {e}", level=messages.ERROR)
            return None
        response = HttpResponse(
            buf.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename="employee_id_cards_table.docx"'
        return response

    export_to_docx_action.short_description = "Export to Word (.docx) [3-Column Table Grid]"

    def generate_qr_action(self, request, queryset):
        generate_qr(self, request, queryset)
        self.message_user(request, f"Generated ID cards for {queryset.count()} employee(s).", messages.SUCCESS)

    generate_qr_action.short_description = "Generate/Update Cards for Selected"

    def download_id_card_action(self, request, queryset):
        generate_qr(self, request, queryset)

        static_dir = os.path.join(settings.BASE_DIR, 'static', 'download')
        in_memory_zip = BytesIO()
        added_files = 0

        with zipfile.ZipFile(in_memory_zip, 'w') as zipf:
            for obj in queryset:
                front = os.path.join(static_dir, f'{obj.employee_id}_front.jpg')
                back = os.path.join(static_dir, f'{obj.employee_id}_back.jpg')

                if os.path.exists(front):
                    zipf.write(front, f'{obj.employee_id}_front.jpg')
                    added_files += 1
                if os.path.exists(back):
                    zipf.write(back, f'{obj.employee_id}_back.jpg')
                    added_files += 1

        if added_files == 0:
            self.message_user(request, "No cards could be generated.", level=messages.ERROR)
            return None

        response = HttpResponse(in_memory_zip.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="employee_cards_images.zip"'
        return response

    download_id_card_action.short_description = "Download Images (ZIP)"

    def download_pdf_a4_action(self, request, queryset):
        generate_qr(self, request, queryset)
        static_dir = os.path.join(settings.BASE_DIR, 'static', 'download')

        pairs = []
        for obj in queryset:
            front = os.path.join(static_dir, f'{obj.employee_id}_front.jpg')
            back = os.path.join(static_dir, f'{obj.employee_id}_back.jpg')
            if os.path.exists(front) and os.path.exists(back):
                dept_name = f" - {obj.department.name}" if obj.department else ""
                pairs.append({
                    'front': front,
                    'back': back,
                    'title': f"{obj.name} ({obj.employee_id}){dept_name}"
                })

        if not pairs:
            self.message_user(request, "Could not generate PDF cards.", level=messages.ERROR)
            return None

        buf = BytesIO()
        if len(pairs) == 1:
            generate_a4_single_card_pdf(pairs[0]['front'], pairs[0]['back'], pairs[0]['title'], buf)
            filename = f"{queryset.first().employee_id}_idcard_a4.pdf"
        else:
            generate_bulk_a4_pdf(pairs, buf)
            filename = f"employees_batch_cards_a4.pdf"

        response = HttpResponse(buf.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    download_pdf_a4_action.short_description = "Download Printable PDF (A4 Sheet)"

    def download_pdf_cr80_action(self, request, queryset):
        generate_qr(self, request, queryset)
        static_dir = os.path.join(settings.BASE_DIR, 'static', 'download')

        if queryset.count() == 1:
            obj = queryset.first()
            front = os.path.join(static_dir, f'{obj.employee_id}_front.jpg')
            back = os.path.join(static_dir, f'{obj.employee_id}_back.jpg')
            buf = BytesIO()
            generate_cr80_pdf(front, back, buf)
            response = HttpResponse(buf.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{obj.employee_id}_cr80_card.pdf"'
            return response
        else:
            # Multi-card CR80 zip of individual PDFs
            buf = BytesIO()
            with zipfile.ZipFile(buf, 'w') as zipf:
                for obj in queryset:
                    front = os.path.join(static_dir, f'{obj.employee_id}_front.jpg')
                    back = os.path.join(static_dir, f'{obj.employee_id}_back.jpg')
                    if os.path.exists(front) and os.path.exists(back):
                        card_buf = BytesIO()
                        generate_cr80_pdf(front, back, card_buf)
                        zipf.writestr(f'{obj.employee_id}_cr80.pdf', card_buf.getvalue())

            response = HttpResponse(buf.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="employees_cr80_cards.zip"'
            return response

    download_pdf_cr80_action.short_description = "Download Plastic Card PDF (CR80 PVC)"

    def export_to_excel_csv(self, request, queryset):
        try:
            fields = [
                'name', 'employee_id', 'department__name', 'dob', 'gender',
                'contact', 'email', 'job_title', 'join_date', 'end_date', 'work_location'
            ]
            df = pd.DataFrame(list(queryset.values(*fields)))
            df.rename(columns={'department__name': 'department'}, inplace=True)
            file_name = "employee_data.csv"

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename={file_name}'
            df.to_csv(response, index=False)
            return response
        except Exception as e:
            self.message_user(request, f'Error exporting data: {str(e)}', level=messages.ERROR)
            return None

    export_to_excel_csv.short_description = "Export Selected to CSV"
    export_to_excel_csv.allowed_permissions = ('change',)


class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'batch', 'enrollment_number', 'course', 'branch',
        'name', 'dob', 'gender', 'contact', 'email',
        'city', 'district', 'state', 'pincode',
        'valid_date_from', 'date_upto', 'location', 'display_image'
    ]
    search_fields = ['name', 'enrollment_number', 'batch', 'course__course_name', 'branch__branch_name']
    list_filter = ['batch', 'course', 'branch', 'gender']
    ordering = ['name', 'enrollment_number', 'valid_date_from', 'date_upto']

    def display_image(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="45" height="45" style="border-radius: 50%; object-fit: cover;">', obj.profile_image.url)
        return "-"

    display_image.short_description = 'Photo'

    actions = [
        'export_to_docx_action',
        'download_pdf_a4_action',
        'download_pdf_cr80_action',
        'download_id_card_action',
        'generate_qr_action',
        'export_to_excel_csv'
    ]

    def export_to_docx_action(self, request, queryset):
        generate_student(self, request, queryset)
        static_dir = os.path.join(settings.BASE_DIR, 'static', 'download')

        pairs = []
        for obj in queryset:
            front = os.path.join(static_dir, f'{obj.enrollment_number}_front.jpg')
            back = os.path.join(static_dir, f'{obj.enrollment_number}_back.jpg')
            if os.path.exists(front) and os.path.exists(back):
                pairs.append({
                    'front': front,
                    'back': back,
                    'title': f"{obj.name} ({obj.enrollment_number})"
                })

        if not pairs:
            self.message_user(request, "Could not generate cards for Word export.", level=messages.ERROR)
            return None

        buf = BytesIO()
        try:
            generate_cards_docx(pairs, buf, back_first=True)
        except ImportError as e:
            self.message_user(request, f"Word export error: {e}", level=messages.ERROR)
            return None
        response = HttpResponse(
            buf.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename="student_id_cards_table.docx"'
        return response

    export_to_docx_action.short_description = "Export to Word (.docx) [3-Column Table Grid]"

    def generate_qr_action(self, request, queryset):
        generate_student(self, request, queryset)
        self.message_user(request, f"Generated ID cards for {queryset.count()} student(s).", messages.SUCCESS)

    generate_qr_action.short_description = "Generate/Update Cards for Selected"

    def download_id_card_action(self, request, queryset):
        generate_student(self, request, queryset)

        static_dir = os.path.join(settings.BASE_DIR, 'static', 'download')
        in_memory_zip = BytesIO()
        added_files = 0

        with zipfile.ZipFile(in_memory_zip, 'w') as zipf:
            for student in queryset:
                front = os.path.join(static_dir, f'{student.enrollment_number}_front.jpg')
                back = os.path.join(static_dir, f'{student.enrollment_number}_back.jpg')

                if os.path.exists(front):
                    zipf.write(front, f'{student.enrollment_number}_front.jpg')
                    added_files += 1
                if os.path.exists(back):
                    zipf.write(back, f'{student.enrollment_number}_back.jpg')
                    added_files += 1

        if added_files == 0:
            self.message_user(request, "No cards could be generated.", level=messages.ERROR)
            return None

        response = HttpResponse(in_memory_zip.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="student_cards_images.zip"'
        return response

    download_id_card_action.short_description = "Download Images (ZIP)"

    def download_pdf_a4_action(self, request, queryset):
        generate_student(self, request, queryset)
        static_dir = os.path.join(settings.BASE_DIR, 'static', 'download')

        pairs = []
        for obj in queryset:
            front = os.path.join(static_dir, f'{obj.enrollment_number}_front.jpg')
            back = os.path.join(static_dir, f'{obj.enrollment_number}_back.jpg')
            if os.path.exists(front) and os.path.exists(back):
                course_name = f" - {obj.course.course_name}" if obj.course else ""
                pairs.append({
                    'front': front,
                    'back': back,
                    'title': f"{obj.name} ({obj.enrollment_number}){course_name}"
                })

        if not pairs:
            self.message_user(request, "Could not generate PDF cards.", level=messages.ERROR)
            return None

        buf = BytesIO()
        if len(pairs) == 1:
            generate_a4_single_card_pdf(pairs[0]['front'], pairs[0]['back'], pairs[0]['title'], buf)
            filename = f"{queryset.first().enrollment_number}_idcard_a4.pdf"
        else:
            generate_bulk_a4_pdf(pairs, buf)
            filename = "students_batch_cards_a4.pdf"

        response = HttpResponse(buf.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    download_pdf_a4_action.short_description = "Download Printable PDF (A4 Sheet)"

    def download_pdf_cr80_action(self, request, queryset):
        generate_student(self, request, queryset)
        static_dir = os.path.join(settings.BASE_DIR, 'static', 'download')

        if queryset.count() == 1:
            obj = queryset.first()
            front = os.path.join(static_dir, f'{obj.enrollment_number}_front.jpg')
            back = os.path.join(static_dir, f'{obj.enrollment_number}_back.jpg')
            buf = BytesIO()
            generate_cr80_pdf(front, back, buf)
            response = HttpResponse(buf.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{obj.enrollment_number}_cr80_card.pdf"'
            return response
        else:
            buf = BytesIO()
            with zipfile.ZipFile(buf, 'w') as zipf:
                for obj in queryset:
                    front = os.path.join(static_dir, f'{obj.enrollment_number}_front.jpg')
                    back = os.path.join(static_dir, f'{obj.enrollment_number}_back.jpg')
                    if os.path.exists(front) and os.path.exists(back):
                        card_buf = BytesIO()
                        generate_cr80_pdf(front, back, card_buf)
                        zipf.writestr(f'{obj.enrollment_number}_cr80.pdf', card_buf.getvalue())

            response = HttpResponse(buf.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="students_cr80_cards.zip"'
            return response

    download_pdf_cr80_action.short_description = "Download Plastic Card PDF (CR80 PVC)"

    def export_to_excel_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Batch', 'Enrollment Number', 'Course', 'Branch', 'Name', 'DOB', 'Gender',
            'Contact', 'Email', 'City', 'District', 'State', 'Pincode',
            'Valid Date From', 'Date Upto', 'Location'
        ])

        for student in queryset:
            writer.writerow([
                student.batch,
                student.enrollment_number,
                student.course.course_name if student.course else "",
                student.branch.branch_name if student.branch else "",
                student.name,
                student.dob,
                student.gender,
                student.contact,
                student.email,
                student.city,
                student.district,
                student.state,
                student.pincode,
                student.valid_date_from,
                student.date_upto,
                student.location,
            ])

        return response

    export_to_excel_csv.short_description = "Export Selected to CSV"


class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_name']
    search_fields = ['course_name']


class BranchAdmin(admin.ModelAdmin):
    list_display = ['branch_name', 'course']
    list_filter = ['course']
    search_fields = ['branch_name', 'course__course_name']


admin.site.register(Department, DepartmentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Branch, BranchAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Student, StudentAdmin)
