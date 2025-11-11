import google.generativeai as genai
import streamlit as st
from datetime import datetime

# Configure Gemini API
genai.configure(api_key="API_KEY")

def generate_practice_questions(context, topic, num_questions=5):
    """Generate practice questions based on course material"""
    
    prompt = f"""
Based on the following course material, generate {num_questions} multiple-choice questions for exam preparation.

Course Material:
{context}

Topic Focus: {topic}

Format each question exactly as:
QUESTION: [question text]
A) [option]
B) [option]
C) [option]
D) [option]
CORRECT: [A/B/C/D]
EXPLANATION: [brief explanation]
---

Generate {num_questions} questions now.
"""
    
    try:
        response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
        questions = parse_quiz_questions(response.text)
        return questions
    except Exception as e:
        st.error(f"Error generating questions: {e}")
        return []

def parse_quiz_questions(text):
    """Parse generated questions into structured format"""
    questions = []
    current_q = {}
    
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('QUESTION:'):
            if current_q:
                questions.append(current_q)
            current_q = {'question': line.replace('QUESTION:', '').strip(), 'options': []}
        elif line.startswith(('A)', 'B)', 'C)', 'D)')):
            current_q['options'].append(line)
        elif line.startswith('CORRECT:'):
            current_q['correct'] = line.replace('CORRECT:', '').strip()
        elif line.startswith('EXPLANATION:'):
            current_q['explanation'] = line.replace('EXPLANATION:', '').strip()
        elif line == '---' and current_q:
            questions.append(current_q)
            current_q = {}
    
    if current_q and 'question' in current_q:
        questions.append(current_q)
    
    return questions

def provide_exam_feedback(score, total):
    """Provide personalized feedback based on exam performance"""
    percentage = (score / total) * 100
    
    if percentage >= 90:
        feedback = "Excellent work! You have a strong grasp of this material. 🌟"
        level = "Advanced"
    elif percentage >= 75:
        feedback = "Good job! You understand most concepts well. Keep practicing! 👍"
        level = "Proficient"
    elif percentage >= 60:
        feedback = "You're making progress. Review the topics you missed and try again. 📚"
        level = "Developing"
    else:
        feedback = "You may need more study time on this topic. Don't worry - learning takes time! 💪"
        level = "Needs Review"
    
    return feedback, level

def update_progress_tracking(topic, score):
    """Update student's progress on specific topics"""
    if topic not in st.session_state.student_profile['exam_scores']:
        st.session_state.student_profile['exam_scores'][topic] = []
    
    st.session_state.student_profile['exam_scores'][topic].append({
        'score': score,
        'date': datetime.now().isoformat()
    })