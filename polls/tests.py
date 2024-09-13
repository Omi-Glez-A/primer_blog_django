import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text, days):
    """
    Crea pregunta
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewsTests(TestCase):
    def test_no_questions(self):
        """
        Si no hay encuesta, muestra mensaje
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No hay encuestas disponibles")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Muestra preguntas con fecha de publicación pasadas en el índice
        """
        question = create_question(question_text="Pregunta pasada.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["lastest_question_list"], [question],)

    def test_future_question(self):
        """
        Crea una encuesta con fecha de publicación futura que no se mostrará en el índice
        """
        create_question(question_text="Pregunta futura.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No hay preguntas disponibles.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])
    
    def test_future_and_past_question(self):
        """
        Aunque existan preguntas pasadas y futuras, solo se mostrarán las pasadas.
        """
        question = create_question(question_text="Pregunta pasada.", days=-30)
        create_question(question_text="Pregunta futura.", days=30)
        response =self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question],)

    def test_two_past_questions(self):
        """
        Mostrar mútliples preguntas en el índice
        """
        question1 = create_question(question_text="Past question 1", days=-30)
        question2 = create_question(question_text="pregunta pasada 2", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question2,question1],)