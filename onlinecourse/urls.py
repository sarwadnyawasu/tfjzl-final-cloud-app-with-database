from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'onlinecourse'

urlpatterns = [
    # Home / course list
    path(route='', view=views.CourseListView.as_view(), name='index'),

    # Enrollment
    path('<int:pk>/detail/', view=views.CourseDetailView.as_view(), name='course_details'),
    path('<int:course_id>/enroll/', view=views.enroll, name='enroll'),

    # Authentication
    path('registration/', view=views.registration_request, name='registration'),
    path('login/', view=views.login_request, name='login'),
    path('logout/', view=views.logout_request, name='logout'),

    # Exam submission — Task 6 required path
    path(
        '<int:course_id>/submission/',
        view=views.submit,
        name='submit'
    ),

    # Exam result — Task 6 required path
    path(
        '<int:course_id>/submission/<int:submission_id>/result/',
        view=views.show_exam_result,
        name='show_exam_result'
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
