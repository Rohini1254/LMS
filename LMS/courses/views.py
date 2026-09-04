from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, request
from django.contrib.auth import update_session_auth_hash
from .models import Course, Module 



from .models import (
    Certificate,
    Course,
    CourseReview,
    Enrollment,
    Lesson,
    LessonProgress,
    Quiz,
    QuizResult,
    CourseRating,
)

@login_required
def teacher_dashboard(request):
    if not hasattr(request.user, "profile") or request.user.profile.role != "teacher":
        return HttpResponse("Access denied. Teachers only.")

    courses = Course.objects.filter(teacher=request.user)

    total_courses = courses.count()

    total_modules = Module.objects.filter(
        course__teacher=request.user
    ).count()

    total_students = Enrollment.objects.filter(
        course__teacher=request.user
    ).values("user").distinct().count()

    return render(
        request,
        "courses/teacher_dashboard.html",
        {
            "courses": courses,
            "total_courses": total_courses,
            "total_modules": total_modules,
            "total_students": total_students,
        }
    )

@login_required
def create_lesson(request, module_id):

    if not hasattr(request.user, "profile") or request.user.profile.role != "teacher":
        return HttpResponse("Access denied. Teachers only.")

    module = get_object_or_404(
        Module,
        id=module_id
    )

    if module.course.teacher != request.user:
        return HttpResponse("You can only add lessons to your own courses.")

    if request.method == "POST":

        title = request.POST.get("title")
        content = request.POST.get("content")

        Lesson.objects.create(
            course=module.course,
            title=title,
            content=content
        )

        return redirect(
            "course_detail",
            course_id=module.course.id
        )

    return render(
        request,
        "courses/create_lesson.html",
        {
            "module": module,
            "course": module.course,
        }
    )



@login_required
def create_course(request):
    if not hasattr(request.user, "profile") or request.user.profile.role != "teacher":
        return HttpResponse("Access denied. Teachers only.")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        price = request.POST.get("price")
        category = request.POST.get("category")

        Course.objects.create(
            title=title,
            description=description,
            price=price,
            category=category,
            teacher=request.user
        )

        return HttpResponse("Course created successfully!")

    return render(request, "courses/create_course.html")

@login_required
def create_module(request, course_id):
    if not hasattr(request.user, "profile") or request.user.profile.role != "teacher":
        return HttpResponse("Access denied. Teachers only.")

    course = get_object_or_404(Course, id=course_id)

    if course.teacher != request.user:
        return HttpResponse("You can only add modules to your own courses.")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        order = request.POST.get("order")

        Module.objects.create(
            course=course,
            title=title,
            description=description,
            order=order
        )

        return redirect("course_detail", course_id=course.id)

    return render(
        request,
        "courses/create_module.html",
        {"course": course}
    )


def course_list(request):
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')

    courses = Course.objects.all()

    if search:
        courses = courses.filter(title__icontains=search)

    if category:
        courses = courses.filter(category=category)

    categories = Course.objects.values_list(
        'category',
        flat=True
    ).distinct()

    return render(
        request,
        'courses/course_list.html',
        {
            'courses': courses,
            'search': search,
            'category': category,
            'categories': categories,
        }
    )


@login_required
def add_review(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        review_text = request.POST.get('review', '')

        CourseReview.objects.create(
            user=request.user,
            course=course,
            rating=rating,
            review=review_text
        )

        return redirect('course_detail', course_id=course.id)

    return render(
        request,
        'courses/add_review.html',
        {'course': course}
    )


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    reviews = CourseReview.objects.filter(course=course)

    enrolled = Enrollment.objects.filter(
        user=request.user,
        course=course
    ).exists()

    return render(
        request,
        'courses/course_detail.html',
        {
            'course': course,
            'reviews': reviews,
            'enrolled': enrolled,
        }
    )


@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )

    return redirect('my_courses')


@login_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(
        user=request.user
    )

    return render(
        request,
        'courses/my_courses.html',
        {'enrollments': enrollments}
    )


@login_required
def dashboard(request):
    enrollments = Enrollment.objects.filter(
        user=request.user
    )

    data = []
    completed_courses = 0

    for enrollment in enrollments:

        course = enrollment.course

        total_lessons = Lesson.objects.filter(
            course=course
        ).count()

        completed_lessons = LessonProgress.objects.filter(
            user=request.user,
            lesson__course=course,
            completed=True
        ).count()

        percent = (
            int(completed_lessons / total_lessons * 100)
            if total_lessons else 0
        )

        quiz = Quiz.objects.filter(
            course=course
        ).first()

        quiz_result = None
        quiz_passed = False

        if quiz:
            quiz_result = QuizResult.objects.filter(
                user=request.user,
                quiz=quiz
            ).order_by('-id').first()

            if quiz_result:
                if quiz_result.total > 0:
                    quiz_passed = (
                        quiz_result.score / quiz_result.total
                    ) >= 0.70

        if percent == 100 and quiz_passed:
            completed_courses += 1

        data.append({
            'course': course,
            'percent': percent,
            'quiz_result': quiz_result,
            'quiz_passed': quiz_passed,
            'lessons_completed': completed_lessons,
            'total_lessons': total_lessons,
        })

    certificates = Certificate.objects.filter(
        user=request.user
    ).count()

    return render(
        request,
        'courses/dashboard.html',
        {
            'progress': data,
            'total_courses': enrollments.count(),
            'completed_courses': completed_courses,
            'certificates': certificates,
        }
    )


@login_required
def complete_lesson(request, lesson_id):

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id
    )

    # Mark lesson as completed
    LessonProgress.objects.update_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'completed': True}
    )

    return redirect(
        'lesson_detail',
        lesson_id=lesson.id
    )

@login_required
def lesson_detail(request, lesson_id):

    lesson = get_object_or_404(Lesson, id=lesson_id)

    lessons = Lesson.objects.filter(
        course=lesson.course
    ).order_by('id')

    completed_lessons = LessonProgress.objects.filter(
        user=request.user,
        lesson__course=lesson.course,
        completed=True
    )

    completed_ids = set(
        completed_lessons.values_list('lesson_id', flat=True)
    )

    total_lessons = lessons.count()
    completed_count = len(completed_ids)

    progress = (
        round((completed_count / total_lessons) * 100)
        if total_lessons > 0
        else 0
    )

    completed = lesson.id in completed_ids

    all_lessons_completed = (
        total_lessons > 0 and
        completed_count == total_lessons
    )

    quiz = Quiz.objects.filter(
        course=lesson.course
    ).first()

    return render(
        request,
        'courses/lesson_detail.html',
        {
            'lesson': lesson,
            'lessons': lessons,
            'completed_ids': completed_ids,
            'completed': completed,
            'completed_count': completed_count,
            'total_lessons': total_lessons,
            'progress': progress,
            'all_lessons_completed': all_lessons_completed,
            'quiz': quiz,
        }
    )
    
@login_required
def quiz_list(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    # Check enrollment
    enrolled = Enrollment.objects.filter(
        user=request.user,
        course=course
    ).exists()

    if not enrolled:
        return redirect(
            'course_detail',
            course_id=course.id
        )

    # Check all lessons completed
    total_lessons = Lesson.objects.filter(
        course=course
    ).count()

    completed_lessons = LessonProgress.objects.filter(
        user=request.user,
        lesson__course=course,
        completed=True
    ).count()

    all_lessons_completed = (
        total_lessons > 0 and
        completed_lessons == total_lessons
    )

    # Quiz is locked until all lessons are completed
    if not all_lessons_completed:
        return redirect('dashboard')

    quiz = Quiz.objects.filter(
        course=course
    ).first()

    if not quiz:
        return redirect('dashboard')

    questions = quiz.questions.all()

    # When student submits quiz
    if request.method == 'POST':

        score = 0
        total = questions.count()

        for question in questions:

            selected_option = request.POST.get(
                f'question_{question.id}'
            )

            if selected_option == question.correct_answer:
                score += 1

        result = QuizResult.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            total=total
        )

        # Passing percentage = 70%
        passed = (
            total > 0 and
            (score / total) >= 0.70
        )

        percentage = (
            round((score / total) * 100, 2)
            if total > 0
            else 0
        )

        return render(
            request,
            'courses/quiz_result.html',
            {
                'course': course,
                'quiz': quiz,
                'score': score,
                'total': total,
                'percentage': percentage,
                'result': result,
                'passed': passed,
            }
        )

    # Show quiz page
    return render(
        request,
        'courses/quiz.html',
        {
            'course': course,
            'quiz': quiz,
            'questions': questions,
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons,
        }
    )


@login_required
def certificate_view(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    # Check all lessons completed
    total_lessons = Lesson.objects.filter(
        course=course
    ).count()

    completed_lessons = LessonProgress.objects.filter(
        user=request.user,
        lesson__course=course,
        completed=True
    ).count()

    all_lessons_completed = (
        total_lessons > 0 and
        completed_lessons == total_lessons
    )

    if not all_lessons_completed:
        return redirect('dashboard')

    # Check quiz
    quiz = Quiz.objects.filter(
        course=course
    ).first()

    if not quiz:
        return redirect('dashboard')

    result = QuizResult.objects.filter(
        user=request.user,
        quiz=quiz
    ).order_by('-id').first()

    if not result:
        return redirect('quiz', course_id=course.id)

    # 70% passing
    passed = (
        result.total > 0 and
        (result.score / result.total) >= 0.70
    )

    if not passed:
        return redirect('dashboard')

    certificate, created = Certificate.objects.get_or_create(
        user=request.user,
        course=course
    )

    return render(
        request,
        'courses/certificate.html',
        {
            'course': course,
            'certificate': certificate
        }
    )


@login_required
def rate_course(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    # Certificate must exist before rating
    certificate_exists = Certificate.objects.filter(
        user=request.user,
        course=course
    ).exists()

    if not certificate_exists:
        return redirect('dashboard')

    if request.method == "POST":

        rating = int(
            request.POST.get("rating", 5)
        )

        CourseRating.objects.update_or_create(
            user=request.user,
            course=course,
            defaults={
                "rating": rating
            }
        )

        return redirect("dashboard")

    return render(request, "courses/create_course.html")


def login_user(request):

    if request.method == 'POST':

        username = request.POST.get(
            'username',
            ''
        ).strip()

        password = request.POST.get(
            'password',
            ''
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('dashboard')

        return render(
            request,
            'courses/login.html',
            {
                'error':
                'Invalid username or password'
            }
        )

    return render(
        request,
        'courses/login.html'
    )


@login_required
def logout_user(request):

    logout(request)

    return redirect('course_list')


@login_required
def logout_confirm(request):

    if request.method == 'POST':

        logout(request)

        return redirect('course_list')

    return render(
        request,
        'courses/logout_confirm.html'
    )


def register_user(request):

    if request.method == 'POST':

        username = request.POST.get(
            'username',
            ''
        ).strip()

        password = request.POST.get(
            'password',
            ''
        )

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                'courses/register.html',
                {
                    'error':
                    'Username already exists.'
                }
            )

        User.objects.create_user(
            username=username,
            password=password
        )

        return redirect('login')

    return render(
        request,
        'courses/register.html'
    )


@login_required
def profile(request):

    if request.method == 'POST':

        request.user.first_name = request.POST.get(
            'first_name',
            ''
        )

        request.user.last_name = request.POST.get(
            'last_name',
            ''
        )

        request.user.email = request.POST.get(
            'email',
            ''
        )

        request.user.save()

    return render(
        request,
        'courses/profile.html',
        {
            'user': request.user
        }
    )


@login_required
def change_password(request):

    if request.method == 'POST':

        current_password = request.POST.get(
            'current_password',
            ''
        )

        new_password = request.POST.get(
            'new_password',
            ''
        )

        if request.user.check_password(
            current_password
        ):

            request.user.set_password(
                new_password
            )

            request.user.save()

            update_session_auth_hash(
                request,
                request.user
            )

            return redirect('profile')

        return render(
            request,
            'courses/change_password.html',
            {
                'error':
                'Current password is incorrect.'
            }
        )

    return render(
        request,
        'courses/change_password.html'
    )

