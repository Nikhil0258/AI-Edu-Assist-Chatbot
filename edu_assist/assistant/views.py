import os
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import ChatHistory, Quiz  # Assuming you have a ChatHistory model
import openai

# Set up your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Import your engineering keywords dictionary
engineering_keywords = {kw.lower() for kw in [
    "Computer Science & Engineering", "Programming Basics", "Programming Languages",
    "C/C++", "Basic Syntax", "Control Structures", "Functions", "Arrays & Pointers",
    "Classes & Objects", "Memory Management", "Python", "Data Types", "Control Flow",
    "Libraries & Packages", "Object-Oriented Programming", "Java", "Exception Handling",
    "Collections Framework", "Multithreading", "JavaScript", "DOM Manipulation", "Events",
    "Async Programming", "ES6+ Features", "Frameworks (React, Angular, Vue)",
    "Basic Tools & Environment", "Development Environment", "IDEs (VS Code, Eclipse, PyCharm)",
    "Code Editors", "Compilers & Interpreters", "Debuggers", "Version Control (Git)",
    "Package Managers", "Web Technologies Basics", "HTML5", "CSS3", "JavaScript Basics",
    "HTTP Protocol", "Web Servers", "API Basics", "Theoretical Concepts", "Computation Theory",
    "Automata Theory & Formal Languages", "Turing Machines & Computability",
    "Computational Complexity", "P vs NP Problem", "Algorithm Analysis", "Graph Theory",
    "Quantum Computing Theory", "Database Theory", "Relational Algebra", "Normalization Theory",
    "Transaction Processing", "Concurrency Control", "Database Recovery", "Query Optimization",
    "Programming Paradigms", "Object-Oriented Theory", "Functional Programming",
    "Logic Programming", "Concurrent Programming", "Distributed Systems Theory", "Type Theory",
    "Core Subjects", "Programming & Data Structures", "Algorithm Design",
    "Data Structure Implementation", "Time & Space Complexity", "File Structures",
    "Index Structures", "Operating Systems", "Process Management", "File Systems",
    "I/O Systems", "Deadlock Handling", "Security & Protection", "Computer Networks",
    "Network Architecture", "Protocol Layers", "Routing Algorithms", "Quality of Service",
    "Wireless Networks", "Trending Technologies", "Artificial Intelligence", "Machine Learning",
    "Deep Learning", "Natural Language Processing", "Computer Vision", "Robotics", "Expert Systems",
    "Cloud Computing", "Virtualization", "Container Technology", "Microservices",
    "Serverless Computing", "Cloud Security", "Edge Computing", "Blockchain", "Cryptography",
    "Smart Contracts", "Distributed Ledger", "Consensus Algorithms", "Cryptocurrency",
    "Blockchain Security", "Important Skills", "Software Development", "Testing Methodologies",
    "DevOps Practices", "Agile Methods", "Code Optimization", "Documentation", "System Design",
    "Architecture Patterns", "Design Patterns", "Scalability", "Performance Optimization",
    "Security Design", "API Design", "Mechanical Engineering", "Basic Tools & Concepts",
    "Engineering Drawing", "Geometric Constructions", "Orthographic Projections",
    "Isometric Views", "Sectional Views", "Dimensioning", "Tolerancing", "Basic Workshop Practice",
    "Measuring Tools", "Vernier Caliper", "Micrometer", "Height Gauge", "Dial Indicators",
    "Hand Tools", "Files", "Hammers", "Chisels", "Screwdrivers", "Machine Tools", "Lathe",
    "Drilling", "Milling", "Grinding", "Basic Materials", "Metals", "Ferrous Metals",
    "Non-ferrous Metals", "Non-metals", "Polymers", "Ceramics", "Composites", "Core Subjects",
    "Mechanics", "Classical Mechanics", "Quantum Mechanics", "Fluid Mechanics",
    "Solid Mechanics", "Kinematics", "Dynamics", "Thermodynamics", "Laws of Thermodynamics",
    "Heat Transfer", "Mass Transfer", "Phase Transitions", "Combustion Theory",
    "Statistical Mechanics", "Materials Science", "Crystal Structure", "Material Properties",
    "Phase Diagrams", "Failure Theories", "Composite Materials", "Nanomaterials",
    "Electrical Engineering", "Circuit Basics", "Voltage, Current, Resistance", "Ohm's Law",
    "Kirchhoff's Laws", "Series & Parallel Circuits", "AC/DC Basics", "Power & Energy",
    "Basic Components", "Resistors", "Types", "Color Coding", "Power Rating", "Capacitors",
    "Charging/Discharging", "Applications", "Inductors", "Properties", "Diodes", "PN Junction",
    "Applications", "Transistors", "BJT", "FET", "Basic Operations", "Measuring Instruments",
    "Multimeter", "Oscilloscope", "Function Generator", "Power Supply", "LCR Meter",
    "Civil Engineering", "Surveying Basics", "Chain Surveying", "Compass Surveying", "Leveling",
    "Theodolite", "Total Station", "GPS Basics", "Construction Materials", "Cement",
    "Types", "Tests", "Aggregates", "Classification", "Properties", "Concrete", "Mix Design",
    "Testing", "Steel", "Applications", "Structural Concepts", "Stress & Strain",
    "Beams & Columns", "Foundations", "Load Types", "Basic Analysis", "Electronics & Communication",
    "Active Components", "ICs", "LEDs", "Passive Components", "Transformers", "Communication Basics",
    "Signals & Systems", "Modulation Types", "Antennas", "Protocols", "Chemical Engineering",
    "Chemistry Fundamentals", "Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry",
    "Analytical Methods", "Lab Techniques", "Safety Protocols", "Basic Unit Operations",
    "Fluid Flow", "Separation Processes", "Mixing", "Size Reduction", "Process Equipment",
    "Pumps", "Heat Exchangers", "Distillation Columns", "Reactors", "Dryers", "Aerospace Engineering",
    "Aircraft Components", "Airframe", "Propulsion", "Landing Gear", "Control Surfaces",
    "Navigation Systems", "Safety Systems", "Aerodynamics Basics", "Airfoil Theory",
    "Lift & Drag", "Flight Controls", "Stability", "Aircraft Performance", "Biomedical Engineering",
    "Medical Electronics", "Sensors", "Filters", "Signal Processing", "Safety Standards",
    "Biomaterials Basics", "Testing Methods", "Compatibility", "Common Engineering Skills",
    "Basic Computer Skills", "Office Tools", "Word Processing", "Spreadsheets", "Presentations",
    "Project Management", "Technical Software", "CAD Basics", "Simulation Tools",
    "Workshop Safety", "Personal Protection", "Equipment Safety", "Emergency Procedures", "Algorithms"
]}

def contains_engineering_keywords(query):
    """Check if the query contains any engineering-related keywords."""
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in engineering_keywords)

# Function to interact with OpenAI API
def chat_with_gpt(messages, max_tokens=150, temperature=0.7):
    """Interacts with OpenAI API and fetches AI response."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Switch to "gpt-4" if preferred
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        # Log the error and return a generic message
        print(f"OpenAI API Error: {e}")
        return "Sorry, I encountered an error. Please try again later."

@csrf_exempt
def edu_assist_view(request):
    """Handles chatbot with keyword filtering."""
    # Initialize chat history in session
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []

    chat_history = request.session['chat_history']
    user_input = request.POST.get("user_textbox", "").strip()
    ai_response = ""

    if user_input:
        if contains_engineering_keywords(user_input):
            # Define GPT conversation context
            messages = [{"role": "system", "content": "You are an AI assistant specializing in engineering."}] + [
                {"role": "user", "content": entry['user']} for entry in chat_history
            ] + [{"role": "assistant", "content": entry['ai']} for entry in chat_history] + [
                {"role": "user", "content": user_input}
            ]
            # Get AI response
            ai_response = chat_with_gpt(messages)
        else:
            # Respond with a generic message for non-engineering queries
            ai_response = "I'm an Engineering Bot. Please ask questions related to engineering."

        # Append to chat history
        chat_history.append({'user': user_input, 'ai': ai_response})

        # Limit chat history size to improve performance
        if len(chat_history) > 5:  # Keep last 20 messages
            chat_history = chat_history[-5:]

        # Update session
        request.session['chat_history'] = chat_history

    return render(request, 'assistant/index.html', {
        'user_input': user_input,
        'ai_response': ai_response,
        'chat_history': chat_history,
    })
def quizzes_view(request):
    topic = request.GET.get('topic', '')
    difficulty = request.GET.get('difficulty', '')
    quizzes = Quiz.objects.filter(topic__icontains=topic, difficulty__icontains=difficulty)

    if request.method == 'POST':
        user_answers = {key: request.POST[key] for key in request.POST if key.startswith('answer_')}
        results = []
        score = 0
        total_questions = len(quizzes)
        for key, user_answer in user_answers.items():
            quiz_id = key.split('_')[-1]  # assuming the format is 'answer_{id}'
            quiz = quizzes.get(pk=quiz_id)
            correct = 'Correct' if int(user_answer) == quiz.correct_option else 'Incorrect'
            if correct == 'Correct':
                score += 1
            results.append({
                'question': quiz.question,
                'user_answer': user_answer,
                'correct_answer': quiz.get_correct_answer_display(),
                'result': correct
            })
        score_percentage = (score / total_questions) * 100
        return render(request, 'assistant/quiz_results.html', {'results': results, 'score': score, 'total_questions': total_questions, 'score_percentage': score_percentage})
    if not quizzes.exists():
        # Generate quizzes if none are available
        Quiz.generate_quiz(topic=topic, difficulty=difficulty, num_questions=5)
        quizzes = Quiz.objects.filter(topic__icontains=topic, difficulty__icontains=difficulty)
    message = None if quizzes else f"No quizzes available for {topic} ({difficulty})."

    return render(request, 'assistant/quizzes.html', {
        'quizzes': quizzes,
        'selected_topic': topic,
        'selected_difficulty': difficulty,
        'message' : message,
    })