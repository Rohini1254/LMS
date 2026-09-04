from django.contrib import admin
from .models import (Course, Enrollment, Lesson, LessonProgress, Question, Quiz, QuizResult, Certificate, CourseReview, UserProfile, Module)

admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Lesson)
admin.site.register(LessonProgress)
admin.site.register(CourseReview)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(QuizResult)
admin.site.register(Certificate)
admin.site.register(UserProfile)
admin.site.register(Module)