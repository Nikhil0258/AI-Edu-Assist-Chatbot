import os
from django.core.management.base import BaseCommand , CommandError
from openai import OpenAI
from assistant.models import Quiz
from django.core.management.base import BaseCommand, CommandError
from assistant.filters import contains_engineering_keywords 
import openai


# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
def get_openai_client():
    import os
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=key)

class Command(BaseCommand):
    help = "Generate quizzes via OpenAI (engineering topics only)"

    def add_arguments(self, parser):
        parser.add_argument("--topic", required=True)
        parser.add_argument("--difficulty", default="Medium")
        parser.add_argument("--num", type=int, default=5)

    def handle(self, *args, **opts):
        topic = (opts["topic"] or "").strip()
        difficulty = (opts["difficulty"] or "").strip()
        num = int(opts["num"])

        if not contains_engineering_keywords(topic):
            raise CommandError(
                "I'm Desh. I answer only engineering-related questions. "
                "Please ask about engineering topics."
            )

        created = Quiz.generate_quiz(topic=topic, difficulty=difficulty, num_questions=num)
        self.stdout.write(self.style.SUCCESS(f"Created {created} question(s)."))