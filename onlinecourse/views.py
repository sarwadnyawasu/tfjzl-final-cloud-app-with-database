from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.shortcuts import redirect
from .models import Course, Enrollment, Question, Choice, Submission
import logging

logger = logging.getLogger(__name__)


def get_course(course_id):
    course = get_object_or_404(Course, pk=course_id)
    return course


def submit(request, course_id):
    """
    Handle exam submission:
    - Get the user and their enrollment for this course
    - Get selected choices from the POST request
    - Create a Submission object linked to the enrollment
    - Attach selected choices to the submission
    - Redirect to the exam result page
    """
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    try:
        enrollment = Enrollment.objects.get(user=user, course=course)
    except Enrollment.DoesNotExist:
        messages.error(request, "You are not enrolled in this course.")
        return redirect('/onlinecourse/')

    # Get list of selected choice IDs from POST data
    selected_ids = request.POST.getlist('choice')

    # Create submission linked to enrollment
    submission = Submission.objects.create(enrollment=enrollment)

    # Add selected choices to the submission
    for choice_id in selected_ids:
        try:
            choice = Choice.objects.get(pk=int(choice_id))
            submission.choices.add(choice)
        except Choice.DoesNotExist:
            logger.warning(f"Choice with id {choice_id} does not exist.")

    submission.save()

    return HttpResponseRedirect(
        f'/onlinecourse/{course_id}/submission/{submission.id}/result/'
    )


def show_exam_result(request, course_id, submission_id):
    """
    Display exam results:
    - Retrieve the course and submission
    - Determine which questions were answered correctly
    - Calculate the total score
    - Render the exam result template
    """
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)

    # Get all selected choice IDs from this submission
    selected_ids = submission.choices.values_list('id', flat=True)

    # Gather all questions from all lessons in the course
    questions = Question.objects.filter(course=course)

    total_score = 0
    max_score = 0
    question_results = []

    for question in questions:
        max_score += question.grade
        # Get selected choices for this specific question
        selected_for_question = submission.choices.filter(question=question).values_list('id', flat=True)
        is_correct = question.is_get_score(list(selected_for_question))
        if is_correct:
            total_score += question.grade

        question_results.append({
            'question': question,
            'is_correct': is_correct,
            'selected_choices': submission.choices.filter(question=question),
        })

    context = {
        'course': course,
        'submission': submission,
        'total_score': total_score,
        'max_score': max_score,
        'question_results': question_results,
        'passed': total_score >= (max_score * 0.8),  # 80% to pass
    }

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
