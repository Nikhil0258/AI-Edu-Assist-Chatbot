import os
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import ChatHistory, Quiz

# Engineering-only gate
from .filters import contains_engineering_keywords

# OpenAI (SDK >= 1.0)
from openai import OpenAI


def get_openai_client():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            key = os.getenv("OPENAI_API_KEY")
        except Exception:
            pass
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=key)


def chat_with_gpt(messages, *, max_tokens=300, temperature=0.7, timeout=30):
    client = get_openai_client()
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        timeout=timeout,
    )
    return r.choices[0].message.content.strip()


# Fixed reply when the input is NOT engineering-related
NOT_ENGINEERING_MSG = (
    "I'm Desh. I answer only engineering-related questions. "
    "Please ask about engineering topics."
)


@csrf_exempt
def chat_view(request):
    """
    Home Chat page with engineering-only gate.
    If the input doesn't contain engineering keywords, we skip OpenAI and
    return NOT_ENGINEERING_MSG.
    """
    chat_history = request.session.setdefault("chat_history", [])
    ai_response = ""

    if request.method == "POST":
        user_input = (request.POST.get("user_textbox") or "").strip()
        if user_input:
            if not contains_engineering_keywords(user_input):
                ai_response = NOT_ENGINEERING_MSG
            else:
                try:
                    # System prompt keeps Desh focused even when the input barely matches.
                    messages = [
                        {
                            "role": "system",
                            "content": (
                                "You are Desh, an assistant that ONLY answers engineering questions "
                                "(software, CS, systems, tooling, devops, etc.). "
                                "If the user asks a non-engineering question, reply exactly: "
                                f"'{NOT_ENGINEERING_MSG}'"
                            ),
                        },
                        {"role": "user", "content": user_input},
                    ]
                    ai_response = chat_with_gpt(messages)
                except Exception as e:
                    ai_response = f"Sorry, I encountered an error: {e}"

            # best-effort persistence
            try:
                ChatHistory.objects.create(user_input=user_input, ai_response=ai_response)
            except Exception:
                pass
            chat_history.append({"user": user_input, "ai": ai_response})
            request.session.modified = True

    return render(
        request,
        "assistant/chat.html",
        {"chat_history": chat_history, "ai_response": ai_response, "active": "chat"},
    )


def quizzes_view(request):
    from .filters import contains_engineering_keywords  # local import to avoid any early import gotchas

    topic = (request.GET.get("topic") or "").strip()
    difficulty = (request.GET.get("difficulty") or "").strip()

    # Normalize for template convenience
    selected_difficulty_lower = difficulty.lower() if difficulty else ""

    # Gate: if a topic is provided and it's not engineering, DO NOT show or create quizzes.
    if topic and not contains_engineering_keywords(topic):
        return render(request, "assistant/quizzes.html", {
            "quizzes": [],
            "selected_topic": topic,
            "selected_difficulty": difficulty,
            "difficulty_easy_selected": selected_difficulty_lower == "easy",
            "difficulty_medium_selected": selected_difficulty_lower == "medium",
            "difficulty_hard_selected": selected_difficulty_lower == "hard",
            "message": (
                "I'm Desh. I answer only engineering-related questions. "
                "Please ask about engineering topics."
            ),
            "active": "quizzes",
        })

    # Normal path (engineering topics or no topic filter yet)
    qs = Quiz.objects.all()
    if topic:
        qs = qs.filter(topic__icontains=topic)
    if difficulty:
        qs = qs.filter(difficulty__icontains=difficulty)
    qs = qs.order_by("id")

    # Grade submitted answers
    if request.method == "POST":
        user_answers = {k: request.POST[k] for k in request.POST if k.startswith("answer_")}
        results, score, total = [], 0, qs.count()
        for key, user_answer in user_answers.items():
            quiz_id = key.split("_")[-1]
            quiz = qs.get(pk=quiz_id)
            idx = int(user_answer)
            is_correct = (idx == quiz.correct_option)
            score += int(is_correct)
            results.append({
                "question": quiz.question,
                "user_answer": quiz.get_option_display(idx),
                "correct_answer": quiz.get_correct_answer_display(),
                "result": "Correct" if is_correct else "Incorrect",
            })
        pct = round((score / total * 100), 2) if total else 0
        return render(request, "assistant/quiz_results.html", {
            "results": results,
            "score": score,
            "total_questions": total,
            "score_percentage": pct,
            "active": "quizzes",
        })

    # Lazy-generate only for engineering topics
    msg = None
    if not qs.exists() and topic and difficulty:
        try:
            created = Quiz.generate_quiz(topic=topic, difficulty=difficulty, num_questions=5)
            if created:
                qs = Quiz.objects.filter(
                    topic__icontains=topic, difficulty__icontains=difficulty
                ).order_by("id")
            else:
                msg = "No questions were generated."
        except ValueError as e:
            # Model enforces the same gate; surface the friendly message
            if "non_engineering_topic" in str(e).lower():
                msg = (
                    "I'm Desh. I answer only engineering-related questions. "
                    "Please ask about engineering topics."
                )
            else:
                msg = str(e)
            qs = Quiz.objects.none()
        except Exception:
            # Keep UI calm on transient errors
            msg = "Unable to generate quizzes right now."
            qs = Quiz.objects.none()

    if msg is None and not qs.exists() and (topic or difficulty):
        msg = f"No quizzes available for {topic} ({difficulty})."

    return render(request, "assistant/quizzes.html", {
        "quizzes": qs,
        "selected_topic": topic,
        "selected_difficulty": difficulty,
        "difficulty_easy_selected": selected_difficulty_lower == "easy",
        "difficulty_medium_selected": selected_difficulty_lower == "medium",
        "difficulty_hard_selected": selected_difficulty_lower == "hard",
        "message": msg,
        "active": "quizzes",
    })


def alarm_view(request):
    return render(request, "assistant/alarm.html", {"active": "alarm"})
