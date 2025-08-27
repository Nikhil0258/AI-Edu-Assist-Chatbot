import os
from django.core.management.base import BaseCommand
from assistant.models import Quiz
import openai


# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


class Command(BaseCommand):
    help = 'Generates quizzes for a specific topic and difficulty using GPT-3.5'

    def add_arguments(self, parser):
        parser.add_argument('topic', type=str, help='The topic for the quiz (e.g., "Java")')
        parser.add_argument('difficulty', type=str, choices=['Easy', 'Medium', 'Hard'], help='The difficulty of the quiz')

    def handle(self, *args, **options):
        topic = options['topic']
        difficulty = options['difficulty']
        self.stdout.write(f'Generating quizzes for {topic} ({difficulty})...')
        
        # Call the generate_quiz method from the Quiz model
        Quiz.generate_quiz(topic=topic, difficulty=difficulty)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully generated quizzes for {topic} ({difficulty})'))
