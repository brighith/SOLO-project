from django.db import models
import re


class TeacherManager(models.Manager):
    def login_validator(self, postData):
        error = {}
        get_emails = Teacher.objects.all()
        if len(postData['teacher_name']) < 5:
            error['teacher_name'] = "Teacher name should be 5 characters or more."

        EMAIL_REGEX = re.compile(
            r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(postData['email']):
            error['email'] = "Invalid email address!"

        for teacher in get_emails:
            if postData['email'] == teacher.email:
                error['email_exists'] = "Email already exists."

        if postData['password'] != postData['conf_password']:
            error['password_conf'] = "Confirmation password does not match."

        if len(postData['password']) < 8:
            error['password'] = "Password must be at least 8 characters."

        return error

    def validate_student(self, postData, section_id):
        error = {}
        if len(postData['student_name']) < 2:
            error['student_name'] = "Student name should be 2 characters or more."
        
        section = Section.objects.get(id=section_id)
        if section.students.all().count() >= 25:
            error['student_number'] = "Maximum number of students is 25."

        return error

    def validate_mark(self, postData, student_id):
        error = {}
        try:
            mark = float(postData['mark'])
            if mark < 0 or mark > 100:
                error['mark'] = "Mark must be between 0 and 100."
        except ValueError:
            error['mark'] = "Invalid mark value. Please enter a valid number."

        return error

    def validate_course(self, postData, student_id):
        error = {}
        if len(postData['course_name']) < 2:
            error['course_name'] = "Course name should be 2 characters or more."

        student = Student.objects.get(id=student_id)
        if student.courses.all().count() >= 5:
            error['course_number'] = "Maximum number of courses is 5."

        return error


class Teacher(models.Model):
    teacher_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = TeacherManager()


class Section(models.Model):
    section_name = models.CharField(max_length=255)
    teacher = models.ForeignKey(Teacher, related_name='sections', on_delete=models.CASCADE)
    objects = TeacherManager()


class Student(models.Model):
    student_name = models.CharField(max_length=255)
    section = models.ForeignKey(Section, related_name='students', on_delete=models.CASCADE)
    objects = TeacherManager()


class Course(models.Model):
    course_name = models.CharField(max_length=255)
    student = models.ForeignKey(Student, related_name='courses', on_delete=models.CASCADE)
    objects = TeacherManager()


class Mark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    mark = models.DecimalField(max_digits=5, decimal_places=2)
    objects = TeacherManager()
