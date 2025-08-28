# AI Edu Assist 
_Django + OpenAI (SDK v1) • Engineering-only chatbot • MCQ quizzes • Lightweight alarm_

A focused study helper for engineering students. **Desh** only answers engineering questions. Non-engineering prompts are gracefully blocked with a friendly message. Includes a quizzes module (generate & auto-grade MCQs) and a simple browser alarm.

## ✨ Features
- **Engineering-only scope**: fast keyword/regex gate (`assistant/filters.py` + `assistant/keywords.py`) + a system prompt — blocks non-engineering queries in **Chat** and **Quizzes** (no API calls wasted).
- **Chatbot**: OpenAI SDK v1 (`gpt-4o-mini`) with timeouts and environment-based config.
- **Quizzes**:
  - Generate MCQs via OpenAI with strict JSON parsing and transactional writes
  - Filter by topic & difficulty; auto-grading with clear results
  - Server + UI both enforce the engineering-only rule
- **UI/UX**: responsive **left sidebar** (Bootstrap 5), persistent chat history, and a small browser **alarm** utility.
- **Security**: `.env` for secrets, `.gitignore` hardened, compatible with GitHub Push Protection.

## 🧭 Project structure
