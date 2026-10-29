# employees/models.py
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    template_code = models.CharField(
        max_length=50,
        choices=[
            ('FACULTY_TEMPLATE', 'Faculty Template'),
            ('GUEST_FACULTY_TEMPLATE', 'Guest Faculty Template'),
            ('WBL_TEMPLATE', 'WBL Template'),
        ],
        default='FACULTY_TEMPLATE',
        help_text="Base card template to use"
    )
    front_template = models.ImageField(upload_to='card_templates/', null=True, blank=True, help_text="Upload custom FRONT template PNG (optional)")
    back_template = models.ImageField(upload_to='card_templates/', null=True, blank=True, help_text="Upload custom BACK template PNG (optional)")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Employee(models.Model):
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    employee_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    contact = models.CharField(max_length=15)
    email = models.EmailField(max_length=255, null=True, unique=True)
    job_title = models.CharField(max_length=100)
    join_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    work_location = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='employee_images/', null=True, blank=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    course_name = models.CharField(max_length=100)

    def __str__(self):
        return self.course_name


class Branch(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    branch_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.branch_name} - {self.course.course_name}"


class Student(models.Model):
    batch = models.IntegerField(
        validators=[
            MaxValueValidator(2200),
            MinValueValidator(2000),
        ]
    )
    enrollment_number = models.CharField(max_length=10, unique=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Course",
        help_text="Select course",
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Branch",
        help_text="Select branch",
    )
    name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    contact = models.CharField(max_length=15)
    email = models.EmailField(max_length=255, null=True, unique=True)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=100)
    valid_date_from = models.DateField(default=timezone.now)
    date_upto = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='employee_images/', null=True, blank=True)

    def __str__(self):
        return self.name
