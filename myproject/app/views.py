from .models import Student, Mark
from django.shortcuts import render, redirect, get_object_or_404
from app.models import *
from django.contrib import messages
import bcrypt


def index(request):
    return render(request, 'index.html')


def registration(request):
    error = Teacher.objects.login_validator(request.POST)
    if len(error) > 0:
        for key, value in error.items():
            messages.error(request, value)
        return redirect('/')
    else:
        password = request.POST['password']
        ps_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        Teacher.objects.create(
            teacher_name=request.POST['teacher_name'], email=request.POST['email'], password=ps_hash
        )
        messages.success(request, "teacher has been created Successfully!")
        return redirect('/')


def login(request):
    teacher = Teacher.objects.filter(email=request.POST['email'])
    if teacher:
        logged_teacher = teacher[0]
        if bcrypt.checkpw(request.POST['password'].encode(), logged_teacher.password.encode()):
            request.session['teacher_id'] = logged_teacher.id
            messages.success(request, " logged in")
            return redirect('/home')
        else:
            messages.error(request, "email / password incorrect")
            return redirect('/')
    else:
        messages.error(request, "email / password incorrect")
        return redirect('/')


def successRedirect(request):
    list(messages.get_messages(request))
    return redirect('/home')


def success(request):
    teacher = Teacher.objects.get(id=request.session['teacher_id'])
    section = Section.objects.all()
    context = {
        'teacher_object': teacher,
        'section_object': section,
        'teacher_session': request.session['teacher_id'],
    }
    return render(request, 'home.html', context)


def logout(request):
    list(messages.get_messages(request))
    request.session.flush()
    return redirect('/')


def newSection(request):
    return render(request, 'new_section.html')


def newSectionRedirect(request):
    list(messages.get_messages(request))
    return redirect('/sections/new')


def sectionCreate(request):
    if request.method == 'POST':
        teacher = Teacher.objects.get(id=request.session['teacher_id'])
        section_name = request.POST.get('section_name', '')
        section = Section.objects.create(section_name=section_name, teacher=teacher)
        messages.success(request, "Section created successfully!")
        return redirect('app:sectionDetails', id=section.id)

    return redirect('app:newSectionRedirect')



def sectionDetails(request, id):
    teacher = get_object_or_404(Teacher, id=request.session.get('teacher_id'))
    section = get_object_or_404(Section, id=id)
    courses = Course.objects.filter(section__id=section.id)  # Filter courses by section_id

    # Fetching students and their marks for each course
    students_and_marks = []
    for course in courses:
        students_in_course = Student.objects.filter(mark__course=course)
        students_and_marks.append({
            'course': course,
            'students': students_in_course,
        })

    context = {
        'teacher_object': teacher,
        'section_object': section,
        'courses': students_and_marks,
        'teacher_session': request.session.get('teacher_id'),
    }

    return render(request, 'section_details.html', context)



def marks(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    students = section.students.all()

    # Get the marks for each student in the section
    marks_data = []
    for student in students:
        marks_data.append({
            'student_name': student.student_name,
            'mark': Mark.objects.filter(student=student).first(),
        })

    context = {
        'section_object': section,
        'marks_data': marks_data,
    }

    return render(request, 'marks.html', context)


def editSection(request, section_id):
    if request.method == 'POST':
        section = Section.objects.get(id=section_id)
        section_name = request.POST.get('section_name', '')  # Use get() with a default value
        section.section_name = section_name
        print(request.POST)  # Check the contents of request.POST
        section.save()

    return redirect('/successRedirect')


def sectionEdit(request, section_id):
    section = get_object_or_404(Section, id=section_id)

    if request.method == 'POST':
        # Check if the logged-in teacher owns this section
        if request.session['teacher_id'] == section.teacher_id:
            # Handle the section update logic here
            section_name = request.POST.get('section_name', '')  # Use get() with a default value
            section.skill_level = request.POST.get('skill_level', '')  # Update other fields as needed
            section.game_day = request.POST.get('game_day', '')  # Update other fields as needed
            section.save()
            return redirect('app:success')  # Redirect to success page or any other appropriate page
        else:
            messages.error(request, "You are not authorized to edit this section.")
            return redirect('app:sectionDetails', id=section_id)

    context = {
        'section_object': section,
    }
    return render(request, 'section_edit.html', context)

def deletesection(request, section_id):
    section = get_object_or_404(Section, id=section_id)

    if request.method == 'POST':
        # Check if the logged-in teacher owns this section
        if request.session['teacher_id'] == section.teacher_id:
            # Handle the section deletion logic here
            section.delete()
            messages.success(request, "Section deleted successfully.")
            return redirect('app:success')
        else:
            messages.error(request, "You are not authorized to delete this section.")
            return redirect('app:sectionDetails', id=section_id)

    context = {
        'section_object': section,
    }
    return render(request, 'section_delete.html', context)


def addStudent(request, section_id):
    error = Student.objects.validate_student(request.POST, section_id)
    if len(error) > 0:
        for key, value in error.items():
            messages.error(request, value)
        return redirect('/sections/' + str(section_id))
    section = Section.objects.get(id=section_id)
    Student.objects.create(
        student_name=request.POST['student_name'], section=section)
    return redirect('/sections/' + str(section_id))


def newCourse(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    return render(request, 'new_course.html', {'section': section})

def createCourse(request, section_id):
    if request.method == 'POST':
        section = get_object_or_404(Section, id=section_id)
        teacher = get_object_or_404(Teacher, id=request.session['teacher_id'])
        course_name = request.POST.get('course_name', '')
        Course.objects.create(course_name=course_name, teacher=teacher, section=section)
        messages.success(request, "Course created successfully!")
        return redirect('app:sectionDetails', id=section_id)
    return redirect('app:newSectionRedirect')

def courseDetails(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    students = course.section.students.all()

    if request.method == 'POST':
        for student in students:
            mark_value = request.POST.get(f'mark_{student.id}')
            try:
                mark = float(mark_value)
                if 0 <= mark <= 100:
                    Mark.objects.update_or_create(student=student, course=course, defaults={'mark': mark})
                    messages.success(request, f"Mark added successfully for {student.student_name} in {course.course_name}")
                else:
                    messages.error(request, f"Invalid mark value for {student.student_name}. Please enter a valid number between 0 and 100.")
            except ValueError:
                messages.error(request, f"Invalid mark value for {student.student_name}. Please enter a valid number between 0 and 100.")

    marks_data = []
    for student in students:
        mark = Mark.objects.filter(student=student, course=course).first()
        marks_data.append({
            'student_name': student.student_name,
            'mark': mark.mark if mark else None,
        })

    context = {
        'course': course,
        'marks_data': marks_data,
    }
    return render(request, 'course_details.html', context)

def add_marks(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        for student in course.student_set.all():
            mark_value = request.POST.get(f'mark_{student.id}')
            try:
                mark = float(mark_value)
                if 0 <= mark <= 100:
                    Mark.objects.create(student=student, course=course, mark=mark)
                else:
                    messages.error(request, f"Invalid mark value for {student.student_name}. Please enter a valid number between 0 and 100.")
            except ValueError:
                messages.error(request, f"Invalid mark value for {student.student_name}. Please enter a valid number between 0 and 100.")
        messages.success(request, f"Marks added successfully for all students in {course.course_name}.")
        return redirect('app:marks', section_id=course.section.id)

    context = {
        'course': course,
        'students': course.student_set.all(),
    }

    return render(request, 'add_marks.html', context)


def add_marks_for_subject(request, section_id, subject_id):
    section = get_object_or_404(Section, id=section_id)
    course = get_object_or_404(Course, id=subject_id, section=section)

    if request.method == 'POST':
        for student in section.students.all():
            mark_value = request.POST.get(f'mark_{student.id}')
            try:
                mark = float(mark_value)
                if 0 <= mark <= 100:
                    Mark.objects.create(student=student, course=course, mark=mark)
                else:
                    messages.error(request, f"Invalid mark value for {student.student_name}. Please enter a valid number between 0 and 100.")
            except ValueError:
                messages.error(request, f"Invalid mark value for {student.student_name}. Please enter a valid number between 0 and 100.")
        messages.success(request, f"Marks added successfully for {course.course_name} in {section.section_name}.")
        return redirect('app:marks', section_id=section_id)

    context = {
        'section': section,
        'course': course,
        'students': section.students.all(),
    }

    return render(request, 'add_marks_subject.html', context)

def deletesection(request, section_id):
    section = Section.objects.get(id=section_id)

    if request.method == 'POST':
        # Delete the section
        section.delete()
        return redirect('app:success')  # Use the 'success' URL pattern

    context = {
        'section': section,
    }
    return render(request, 'section_delete.html', context)