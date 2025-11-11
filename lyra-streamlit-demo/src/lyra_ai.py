import google.generativeai as genai
import streamlit as st
from datetime import datetime

# Configure Gemini API
genai.configure(api_key="API_KEY")

def generate_personalized_answer(context, query, student_profile):
    """Generate answer adapted to student's learning pace and history"""
    
    learning_pace = student_profile['learning_pace']
    
    pace_instructions = {
        'fast': "Be concise and technical. The student learns quickly.",
        'moderate': "Balance detail and clarity. Use examples when helpful.",
        'slow': "Be very detailed and use multiple examples. Break down complex concepts step by step."
    }
    
    prompt = f"""
You are Lyra, an AI-powered study assistant. You provide personalized, adaptive learning support.

Student Learning Profile:
- Learning Pace: {learning_pace}
- Total Interactions: {student_profile['interaction_count']}
- Known Gaps: {', '.join(student_profile['knowledge_gaps'][-3:]) if student_profile['knowledge_gaps'] else 'None identified yet'}

Instructions: {pace_instructions[learning_pace]}

Course Context:
{context}

Student Question: {query}

Provide a clear, accurate answer. If this topic relates to any known knowledge gaps, gently reinforce those concepts. End with a brief follow-up question to check understanding (optional, only if appropriate).
"""
    
    response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
    return response.text

def analyze_learning_patterns(query, answer_quality=None):
    """Track student's learning patterns and identify knowledge gaps"""
    st.session_state.student_profile['interaction_count'] += 1
    
    # Extract topic from query (simple keyword extraction)
    topics = extract_topics(query)
    
    # Record study session
    st.session_state.student_profile['study_history'].append({
        'timestamp': datetime.now().isoformat(),
        'query': query,
        'topics': topics
    })
    
    # Adjust learning pace based on interaction patterns
    if st.session_state.student_profile['interaction_count'] > 10:
        recent_sessions = st.session_state.student_profile['study_history'][-10:]
        avg_time_between = calculate_avg_study_frequency(recent_sessions)
        
        if avg_time_between < 3600:  # Less than 1 hour
            st.session_state.student_profile['learning_pace'] = 'fast'
        elif avg_time_between > 86400:  # More than 1 day
            st.session_state.student_profile['learning_pace'] = 'slow'

def extract_topics(query):
    """Simple topic extraction (can be enhanced with NLP)"""
    keywords = query.lower().split()
    stop_words = {'what', 'how', 'why', 'when', 'where', 'is', 'are', 'the', 'a', 'an'}
    return [word for word in keywords if word not in stop_words and len(word) > 3]

def calculate_avg_study_frequency(sessions):
    """Calculate average time between study sessions"""
    if len(sessions) < 2:
        return 0
    times = [datetime.fromisoformat(s['timestamp']) for s in sessions]
    diffs = [(times[i+1] - times[i]).total_seconds() for i in range(len(times)-1)]
    return sum(diffs) / len(diffs) if diffs else 0

def identify_knowledge_gaps(context, query, answer):
    """Use AI to identify potential knowledge gaps"""
    gap_prompt = f"""
    Analyze this student interaction and identify any knowledge gaps:
    
    Question: {query}
    Context available: {context[:500]}...
    Answer given: {answer}
    
    List 1-3 specific topics the student might need to review. Be concise.
    Format: Just list the topics, one per line.
    """
    
    try:
        response = genai.GenerativeModel("gemini-2.0-flash-exp").generate_content(gap_prompt)
        gaps = [line.strip() for line in response.text.split('\n') if line.strip()]
        return gaps[:3]
    except:
        return []