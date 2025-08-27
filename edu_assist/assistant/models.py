import os
from django.db import models
import openai
import openai.error
from openai.error import OpenAIError
import re
# Create your models here.

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
    "Workshop Safety", "Personal Protection", "Equipment Safety", "Emergency Procedures"
]}

unique_topics = sorted({kw.split(" ")[0] for kw in engineering_keywords})  # Generate unique topics

class Quiz(models.Model):
    """Model to represent quizzes."""
    topic = models.CharField(max_length=100, choices=[(topic, topic) for topic in unique_topics])
    difficulty = models.CharField(max_length=10, choices=[("Easy", "Easy"), ("Medium", "Medium"), ("Hard", "Hard")])
    question = models.TextField()
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    correct_option = models.IntegerField()
    def __str__(self):
        return f"{self.topic} ({self.difficulty}): {self.question[:50]}"
    
    def get_correct_answer_display(self):
        correct_option_number = self.correct_option
        return getattr(self, f'option{correct_option_number}')
    
    @classmethod
    def generate_quiz(cls, topic, difficulty, num_questions=5):
        existing_quizzes = cls.objects.filter(topic__icontains=topic, difficulty=difficulty)
        if existing_quizzes.exists():
            print(f"Quizzes for {topic} ({difficulty}) already exist.")
            return

        messages = [
            {"role": "system", "content": "You are an assistant that generates multiple-choice quiz questions in a specific format."},
            {"role": "user", "content": f"Generate {num_questions} multiple-choice questions on the topic '{topic}' with a difficulty level of '{difficulty}'. Please follow this strict format for each question:\n\nQuestion: [question text]\nA) [option 1]\nB) [option 2]\nC) [option 3]\nD) [option 4]\nCorrect Option: [A/B/C/D]"}
        ]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            generated_text = response['choices'][0]['message']['content'].strip()
            print(f"API Response: {generated_text}")  # Debugging: output raw API response

            if not generated_text:
                print("No content generated by the API.")
                return

            # Split the response into individual questions
            questions_raw = generated_text.split("\n\n")
            question_data = []

            for question_block in questions_raw:
                if not question_block.strip():
                    continue

                # Parse each question block
                lines = question_block.strip().split("\n")
                if len(lines) >= 6:  # Ensure we have all required components
                    question = lines[0].replace("Question:", "").strip()
                    options = [
                        lines[1].replace("A)", "").strip(),
                        lines[2].replace("B)", "").strip(),
                        lines[3].replace("C)", "").strip(),
                        lines[4].replace("D)", "").strip()
                    ]
                    correct_option = lines[5].replace("Correct Option:", "").strip()
                    
                    # Convert letter option to number (1-4)
                    correct_option_num = {"A": 1, "B": 2, "C": 3, "D": 4}.get(correct_option)
                    
                    if correct_option_num:
                        question_data.append({
                            'question': question,
                            'options': options,
                            'correct_option': correct_option_num,
                        })

            if not question_data:
                print("No valid questions parsed.")
                return

            # Save the questions to the database
            for data in question_data:
                cls.objects.create(
                    topic=topic,
                    difficulty=difficulty,
                    question=data['question'],
                    option1=data['options'][0],
                    option2=data['options'][1],
                    option3=data['options'][2],
                    option4=data['options'][3],
                    correct_option=data['correct_option'],
                )
                print(f"Saved quiz: {data['question']}")

            print(f"Successfully generated and saved {len(question_data)} questions.")

        except OpenAIError as e:
            print(f"OpenAI API error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            
class ChatHistory(models.Model):
    user_input = models.TextField()
    ai_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp}: {self.user_input}"
