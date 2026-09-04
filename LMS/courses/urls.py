from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('lesson/<int:lesson_id>/complete/', views.complete_lesson, name='complete_lesson'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('quiz/<int:course_id>/', views.quiz_list, name='quiz'),
    path('course/<int:course_id>/certificate/', views.certificate_view, name='certificate'),
    path('profile/', views.profile, name='profile'),
    path('course/<int:course_id>/review/', views.add_review, name='add_review'),
    path('change-password/', views.change_password, name='change_password'),
    path('logout-confirm/', views.logout_confirm, name='logout_confirm'),
    path('logout/', views.logout_user, name='logout_user'),
    path("rate-course/<int:course_id>/", views.rate_course, name="rate_course"),
    path("create-course/", views.create_course, name="create_course"),
    path("course/<int:course_id>/create-module/", views.create_module, name="create_module"),  
    path("module/<int:module_id>/create-lesson/", views.create_lesson, name="create_lesson"),
    path("teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    path("lesson/<int:lesson_id>/", views.lesson_detail, name="lesson_detail"),

   

]