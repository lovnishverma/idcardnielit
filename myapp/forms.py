from django import forms
from .models import Employee, Student, Branch, Course, Department
from django.contrib.auth.models import User

class EmployeeForm(forms.ModelForm):
    GENDER_CHOICES = (
        ('', 'Select'),
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    WORK_LOC_CHOICES = (
        ('', 'Select'),
        ('Ropar, Punjab 140001', 'Ropar, Punjab 140001'),
        ('Chandigarh, Punjab 160030', 'Chandigarh, Punjab 160030'),
    )

    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label='Select Department',
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'department'
        })
    )

    class Meta:
        model = Employee
        fields = '__all__'

        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}, format='%d/%m/%Y'),
            'join_date': forms.DateInput(attrs={'type': 'date'}, format='%d/%m/%Y'),
            'end_date': forms.DateInput(attrs={'type': 'date'}, format='%d/%m/%Y'),
            # Add any other date fields you want to format here
        }

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)

        # Department queryset updated dynamically
        self.fields['department'].queryset = Department.objects.all()

        # Example for CharField (employee_id)
        self.fields['employee_id'].widget.attrs.update({
            'class': 'form-control',
            'id': 'employee_id',
            'type': 'text',
            # Add any other attributes you want
        })
        self.fields['employee_id'].required = True

        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'id': 'name',
            'type': 'text',
            # Add any other attributes you want
        })
        self.fields['name'].required = True

        # Repeat the above process for each field in your form

        # Example for DateField (dob)
        self.fields['dob'].widget.attrs.update({
            'class': 'form-control',
            'id': 'dob',
            'type': 'date'
            # Add any other attributes you want
        })
        self.fields['dob'].required = True

        self.fields['gender'] = forms.ChoiceField(
            choices=self.GENDER_CHOICES,
            widget=forms.Select(attrs={
                'class': 'form-control',
                'id': 'gender',
                'type': 'text',
                # Add any other attributes you want
            })
        )
        self.fields['gender'].required = True

        self.fields['contact'].widget.attrs.update({
            'class': 'form-control',
            'id': 'contact',
            'type': 'text',
            # Add any other attributes you want
        })
        self.fields['contact'].required = True

        # Example for EmailField (email)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'id': 'email',
            'type': 'email',
            # Add any other attributes you want
        })
        self.fields['email'].required = True

        # Example for ImageField (profile_image)
        self.fields['profile_image'].widget.attrs.update({
            'class': 'form-control',
            'id': 'profile_image',
            'type': 'file',
            # Add any other attributes you want
        })
        self.fields['profile_image'].required = True

        self.fields['job_title'].widget.attrs.update({
            'class': 'form-control',
            'id': 'job_title',
            'type': 'file',
            # Add any other attributes you want
        })
        self.fields['job_title'].required = True

        self.fields['join_date'].widget.attrs.update({
            'class': 'form-control',
            'id': 'join_date',
            'type': 'date',
            # Add any other attributes you want
        })
        self.fields['join_date'].required = True

        self.fields['end_date'].widget.attrs.update({
            'class': 'form-control',
            'id': 'end_date',
            'type': 'date',
            # Add any other attributes you want
        })
        self.fields['end_date'].required = False

        self.fields['work_location'] = forms.ChoiceField(
            choices=self.WORK_LOC_CHOICES,
            widget=forms.Select(attrs={
                'class': 'form-control',
                'id': 'work_location',
                'type': 'text',
                # Add any other attributes you want
            })
        )
        self.fields['work_location'].required = True


        # Repeat for other fields in your form


class StudentForm(forms.ModelForm):
    LOC_CHOICES = (
        ('', 'Select'),
        ('Ropar, Punjab 140001', 'Ropar, Punjab 140001'),
        ('Chandigarh, Punjab 160030', 'Chandigarh, Punjab 160030'),
    )

    GENDER_CHOICES = (
        ('', 'Select'),
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    class Meta:
        model = Student
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}, format='%d/%m/%Y'),
            'join_date': forms.DateInput(attrs={'type': 'date'}, format='%d/%m/%Y'),
            'end_date': forms.DateInput(attrs={'type': 'date'}, format='%d/%m/%Y'),
            # Add any other date fields you want to format here
        }
        fields = [
            'batch',
            'enrollment_number',
            'course',
            'branch',
            'name',
            'dob',
            'gender',
            'contact',
            'email',
            'city',
            'district',
            'state',
            'pincode',
            'location',
            'profile_image']

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)

        self.fields['batch'].widget.attrs.update({
            'class': 'form-control',
            'id': 'batch',
            'type': 'number',
            # Add any other attributes you want
        })

        self.fields['enrollment_number'].widget.attrs.update({
            'class': 'form-control',
            'id': 'enrollment_number',
            'type': 'text',
            # Add any other attributes you want
        })

        self.fields['course'].widget.attrs.update({
            'class': 'form-control',
            'id': 'course',
            'empty_label': None

        })

        self.fields['branch'].widget.attrs.update({
            'class': 'form-control',
            'id': 'branch',
            'empty_label': None
        })

        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'id': 'name',
            'type': 'text',
            # Add any other attributes you want
        })

        self.fields['dob'].widget.attrs.update({
            'class': 'form-control',
            'id': 'dob',
            'type': 'date',
            # Add any other attributes you want
        })

        self.fields['gender'] = forms.ChoiceField(
            choices=self.GENDER_CHOICES,
            widget=forms.Select(attrs={
                'class': 'form-control',
                'id': 'gender',
                'type': 'text',
                # Add any other attributes you want
            })
        )
        self.fields['contact'].required = True

        self.fields['contact'].widget.attrs.update({
            'class': 'form-control',
            'id': 'contact',
            'type': 'text',
            # Add any other attributes you want
        })

        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'id': 'email',
            'type': 'email',
            # Add any other attributes you want
        })

        self.fields['city'].widget.attrs.update({
            'class': 'form-control',
            'id': 'city',
            'type': 'text',
            # Add any other attributes you want
        })

        self.fields['district'].widget.attrs.update({
            'class': 'form-control',
            'id': 'district',
            'type': 'text',
            # Add any other attributes you want
        })

        self.fields['state'].widget.attrs.update({
            'class': 'form-control',
            'id': 'state',
            'type': 'text',
            # Add any other attributes you want
        })

        self.fields['pincode'].widget.attrs.update({
            'class': 'form-control',
            'id': 'pincode',
            'type': 'text',
            # Add any other attributes you want
        })

        self.fields['location'] = forms.ChoiceField(
            choices=self.LOC_CHOICES,
            widget=forms.Select(attrs={
                'class': 'form-control',
                'id': 'location',
            })
        )
        self.fields['location'].required = True

        self.fields['profile_image'].widget.attrs.update({
            'class': 'form-control',
            'id': 'profile_image',
            'type': 'file',
            # Add any other attributes you want
        })





class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_name']


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['course', 'branch_name']
