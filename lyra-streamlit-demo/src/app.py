import streamlit as st
from datetime import datetime
import time
from lyra_ai import (
    generate_personalized_answer, 
    analyze_learning_patterns, 
    identify_knowledge_gaps
)
from vector_store import create_vector_store, retrieve_relevant_chunks
from quiz import (
    generate_practice_questions, 
    provide_exam_feedback, 
    update_progress_tracking,
    parse_quiz_questions
)
from utils import chunk_text

# ===============================
# Session State Initialization
# ===============================
if 'student_profile' not in st.session_state:
    st.session_state.student_profile = {
        'knowledge_gaps': [],
        'strong_topics': [],
        'interaction_count': 0,
        'learning_pace': 'moderate',
        'study_history': [],
        'exam_scores': {}
    }

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'current_mode' not in st.session_state:
    st.session_state.current_mode = 'Q&A'

if 'quiz_active' not in st.session_state:
    st.session_state.quiz_active = False
    st.session_state.quiz_questions = []
    st.session_state.quiz_score = 0
    st.session_state.current_question_idx = 0

# Pre-assessment timer states
if 'assessment_mode' not in st.session_state:
    st.session_state.assessment_mode = False
    st.session_state.assessment_start_time = None
    st.session_state.assessment_answers = {}
    st.session_state.assessment_submitted = False

# ===============================
# Helper Functions
# ===============================
def display_progress_dashboard():
    """Show student's learning progress"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Your Learning Progress")
    
    profile = st.session_state.student_profile
    
    st.sidebar.metric("Study Sessions", profile['interaction_count'])
    st.sidebar.metric("Learning Pace", profile['learning_pace'].title())
    
    if profile['exam_scores']:
        st.sidebar.write("**Recent Quiz Scores:**")
        for topic, scores in list(profile['exam_scores'].items())[-3:]:
            if scores:
                latest_score = scores[-1]['score']
                st.sidebar.write(f"• {topic}: {latest_score}%")
    
    if profile['knowledge_gaps']:
        st.sidebar.write("**Focus Areas:**")
        for gap in profile['knowledge_gaps'][-3:]:
            st.sidebar.write(f"• {gap}")

# ===============================
# Main Streamlit UI
# ===============================
st.set_page_config(page_title="Lyra - AI Study Assistant", page_icon="🎓", layout="wide")

# Header
st.title("🎓 Lyra - Your AI Study Assistant")
st.markdown("*Personalized learning support available 24/7*")

# Sidebar - Mode Selection
st.sidebar.title("Learning Modes")
mode = st.sidebar.radio(
    "Choose your learning mode:",
    ["💬 Q&A Support", "📝 Exam Preparation", "📊 Progress Review", "🎯 Pre-Assessment"]
)

# Display progress dashboard
display_progress_dashboard()

# File Upload
uploaded_files = st.file_uploader(
    "📚 Upload your course materials (.txt files)", 
    accept_multiple_files=True, 
    type=["txt"]
)

if uploaded_files:
    # Load and process documents
    text_data = ""
    for file in uploaded_files:
        text_data += file.read().decode("utf-8") + "\n"
    
    with st.spinner("Processing course materials..."):
        chunks = chunk_text(text_data)
        embeddings, vectorizer, chunks = create_vector_store(chunks)
    
    st.success(f"✅ Loaded {len(chunks)} sections from your course materials")
    
    # Mode-specific interfaces
    if mode == "💬 Q&A Support":
        st.subheader("Ask Questions About Your Course")
        st.write("I'm here to help you understand your course material. Ask me anything!")
        
        query = st.text_input("Your question:", key="qa_input")
        
        if query:
            with st.spinner("Thinking..."):
                # Retrieve context - now returns list of tuples
                results = retrieve_relevant_chunks(query, embeddings, vectorizer, chunks)
                context = "\n\n".join([chunk for chunk, score in results])
                
                answer = generate_personalized_answer(context, query, st.session_state.student_profile)
                
                # Analyze and track learning
                analyze_learning_patterns(query)
                gaps = identify_knowledge_gaps(context, query, answer)
                
                if gaps:
                    st.session_state.student_profile['knowledge_gaps'].extend(gaps)
                
                st.markdown("### 📖 Answer:")
                st.write(answer)
                
                # Store conversation
                st.session_state.conversation_history.append({
                    'query': query,
                    'answer': answer,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Show related topics
                if gaps:
                    with st.expander("💡 Suggested Review Topics"):
                        for gap in gaps:
                            st.write(f"• {gap}")
    
    elif mode == "📝 Exam Preparation":
        st.subheader("Practice for Your Exam")
        st.write("Generate personalized practice questions based on your course material.")
        
        topic = st.text_input("Enter topic for practice questions:", key="exam_topic")
        num_questions = st.slider("Number of questions:", 3, 10, 5)
        
        if st.button("Generate Practice Quiz"):
            with st.spinner("Creating your personalized quiz..."):
                results = retrieve_relevant_chunks(topic, embeddings, vectorizer, chunks, top_k=5)
                context = "\n\n".join([chunk for chunk, score in results])
                questions = generate_practice_questions(context, topic, num_questions)
                
                if questions:
                    st.session_state.quiz_questions = questions
                    st.session_state.quiz_active = True
                    st.session_state.current_question_idx = 0
                    st.session_state.quiz_score = 0
                    st.session_state.quiz_answers = []
                    st.rerun()
        
        # Display quiz
        if st.session_state.quiz_active and st.session_state.quiz_questions:
            questions = st.session_state.quiz_questions
            idx = st.session_state.current_question_idx
            
            if idx < len(questions):
                q = questions[idx]
                st.markdown(f"### Question {idx + 1} of {len(questions)}")
                st.write(q['question'])
                
                answer = st.radio("Select your answer:", q['options'], key=f"q_{idx}")
                
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.button("Submit Answer"):
                        correct_letter = q['correct']
                        selected_letter = answer[0] if answer else ""
                        
                        if selected_letter == correct_letter:
                            st.success("✅ Correct!")
                            st.session_state.quiz_score += 1
                        else:
                            st.error(f"❌ Incorrect. The correct answer is {correct_letter}")
                        
                        st.info(f"💡 {q.get('explanation', 'No explanation available')}")
                        
                        st.session_state.quiz_answers.append({
                            'question': q['question'],
                            'selected': selected_letter,
                            'correct': correct_letter,
                            'is_correct': selected_letter == correct_letter
                        })
                        
                        time.sleep(3)
                        st.session_state.current_question_idx += 1
                        
                        if st.session_state.current_question_idx >= len(questions):
                            score = st.session_state.quiz_score
                            total = len(questions)
                            percentage = (score / total) * 100
                            
                            feedback, level = provide_exam_feedback(score, total)
                            update_progress_tracking(topic, percentage)
                            
                            st.balloons()
                            st.markdown("---")
                            st.markdown("### 🎉 Quiz Complete!")
                            st.metric("Your Score", f"{score}/{total} ({percentage:.1f}%)")
                            st.write(feedback)
                            st.write(f"**Proficiency Level:** {level}")
                            
                            if st.button("Take Another Quiz"):
                                st.session_state.quiz_active = False
                                st.rerun()
                        else:
                            st.rerun()
    
    elif mode == "📊 Progress Review":
        st.subheader("Your Learning Journey")
        
        profile = st.session_state.student_profile
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Study Sessions", profile['interaction_count'])
        with col2:
            st.metric("Learning Pace", profile['learning_pace'].title())
        with col3:
            avg_score = 0
            if profile['exam_scores']:
                all_scores = [s['score'] for scores in profile['exam_scores'].values() for s in scores]
                avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
            st.metric("Average Quiz Score", f"{avg_score:.1f}%")
        
        st.markdown("---")
        
        if profile['exam_scores']:
            st.subheader("📈 Quiz Performance by Topic")
            for topic, scores in profile['exam_scores'].items():
                with st.expander(f"📚 {topic}"):
                    for i, score_data in enumerate(scores, 1):
                        date = datetime.fromisoformat(score_data['date']).strftime("%Y-%m-%d %H:%M")
                        st.write(f"Attempt {i}: {score_data['score']}% - {date}")
        
        if profile['study_history']:
            st.subheader("📅 Recent Study Sessions")
            recent = profile['study_history'][-5:]
            for session in reversed(recent):
                date = datetime.fromisoformat(session['timestamp']).strftime("%Y-%m-%d %H:%M")
                st.write(f"• {date}: {session['query'][:50]}...")
        
        if profile['knowledge_gaps']:
            st.subheader("🎯 Recommended Focus Areas")
            unique_gaps = list(set(profile['knowledge_gaps']))[-5:]
            for gap in unique_gaps:
                st.write(f"• {gap}")
    
    elif mode == "🎯 Pre-Assessment":
        st.subheader("Test Your Current Knowledge")
        st.write("Take a timed assessment to identify what you already know and where to focus your studies.")
        st.info("⏱️ **Timer:** You'll have 1 minute per question. No feedback until you submit!")
        
        # Check if assessment is submitted - show results
        if st.session_state.assessment_submitted:
            questions = st.session_state.quiz_questions
            user_answers = st.session_state.assessment_answers
            
            # Calculate score
            score = 0
            for idx, q in enumerate(questions):
                user_answer = user_answers.get(idx, "")
                if user_answer and user_answer[0] == q['correct']:
                    score += 1
            
            total = len(questions)
            percentage = (score / total) * 100
            
            feedback, level = provide_exam_feedback(score, total)
            assess_topic = st.session_state.get('current_assessment_topic', 'Pre-Assessment')
            update_progress_tracking(assess_topic, percentage)
            
            st.balloons()
            st.markdown("---")
            st.markdown("## 🎉 Assessment Complete!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score", f"{score}/{total}")
            with col2:
                st.metric("Percentage", f"{percentage:.1f}%")
            with col3:
                st.metric("Level", level)
            
            st.write(feedback)
            st.markdown("---")
            
            # Show detailed results
            st.markdown("### 📋 Detailed Results")
            
            for idx, q in enumerate(questions):
                user_answer = user_answers.get(idx, "No answer provided")
                correct_letter = q['correct']
                user_letter = user_answer[0] if user_answer and user_answer != "No answer provided" else ""
                is_correct = user_letter == correct_letter
                
                if is_correct:
                    st.success(f"**Question {idx + 1}:** ✅ Correct")
                else:
                    st.error(f"**Question {idx + 1}:** ❌ Incorrect")
                
                st.write(f"**Q:** {q['question']}")
                
                # Show all options with highlighting
                st.write("**Options:**")
                for option in q['options']:
                    option_letter = option[0]
                    if option_letter == correct_letter and option_letter == user_letter:
                        st.markdown(f"✅ **{option}** ← Your answer (Correct!)")
                    elif option_letter == correct_letter:
                        st.markdown(f"✅ **{option}** ← Correct answer")
                    elif option_letter == user_letter:
                        st.markdown(f"❌ {option} ← Your answer")
                    else:
                        st.write(f"   {option}")
                
                st.info(f"💡 **Explanation:** {q.get('explanation', 'No explanation available')}")
                st.markdown("---")
            
            st.success("💡 **Recommendation:** Review the topics where you answered incorrectly and use the Q&A mode for deeper understanding!")
            
            # Reset button
            if st.button("Take Another Assessment", key="reset_assessment"):
                st.session_state.assessment_mode = False
                st.session_state.assessment_submitted = False
                st.session_state.assessment_answers = {}
                st.session_state.quiz_questions = []
                st.rerun()
        
        # Check if assessment is active - show questions with timer
        elif st.session_state.assessment_mode and st.session_state.quiz_questions:
            questions = st.session_state.quiz_questions
            total_questions = len(questions)
            time_limit_seconds = total_questions * 60  # 1 minute per question
            
            # Calculate elapsed and remaining time
            elapsed_time = (datetime.now() - st.session_state.assessment_start_time).total_seconds()
            remaining_time = max(0, time_limit_seconds - elapsed_time)
            
            # Display timer
            minutes_left = int(remaining_time // 60)
            seconds_left = int(remaining_time % 60)
            
            # Timer display with color coding
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if remaining_time > 60:
                    st.markdown(f"### ⏱️ {minutes_left}:{seconds_left:02d}")
                elif remaining_time > 0:
                    st.markdown(f"### ⚠️ {minutes_left}:{seconds_left:02d}")
                else:
                    st.markdown(f"### ⏰ Time's Up!")
            
            # Progress bar
            progress = 1 - (remaining_time / time_limit_seconds)
            st.progress(progress)
            
            # Auto-submit if time is up
            if remaining_time <= 0:
                st.warning("⏰ Time's up! Your assessment has been automatically submitted.")
                st.session_state.assessment_submitted = True
                st.session_state.assessment_mode = False
                st.rerun()
            
            st.markdown("---")
            st.markdown(f"### Answer all {total_questions} questions")
            st.write("**Note:** You won't see if answers are correct or incorrect until you submit!")
            st.markdown("---")
            
            # Display all questions at once
            for idx, q in enumerate(questions):
                st.markdown(f"**Question {idx + 1}:**")
                st.write(q['question'])
                
                # Get previously selected answer if exists
                default_index = 0
                if idx in st.session_state.assessment_answers:
                    saved_answer = st.session_state.assessment_answers[idx]
                    for i, opt in enumerate(q['options']):
                        if opt == saved_answer:
                            default_index = i
                            break
                
                # Radio button for answer selection
                selected = st.radio(
                    "Select your answer:",
                    q['options'],
                    key=f"assess_q_{idx}",
                    index=default_index
                )
                
                # Store the answer
                st.session_state.assessment_answers[idx] = selected
                
                st.markdown("---")
            
            # Submit button
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("📝 Submit Assessment", type="primary", use_container_width=True):
                    st.session_state.assessment_submitted = True
                    st.session_state.assessment_mode = False
                    st.rerun()
            
            # Auto-refresh to update timer
            time.sleep(1)
            st.rerun()
        
        else:
            # Show start screen
            assessment_topic = st.text_input("What topic would you like to assess?", key="assess_topic")
            num_questions = st.slider("Number of questions:", 5, 15, 10, key="num_assess_q")
            
            st.info(f"⏱️ You will have **{num_questions} minutes** to complete this assessment ({num_questions} questions × 1 minute each)")
            
            if st.button("Start Pre-Assessment", type="primary") and assessment_topic:
                with st.spinner("Generating assessment..."):
                    results = retrieve_relevant_chunks(assessment_topic, embeddings, vectorizer, chunks, top_k=7)
                    context = "\n\n".join([chunk for chunk, score in results])
                    questions = generate_practice_questions(context, assessment_topic, num_questions)
                    
                    if questions:
                        st.session_state.quiz_questions = questions
                        st.session_state.assessment_mode = True
                        st.session_state.assessment_start_time = datetime.now()
                        st.session_state.assessment_answers = {}
                        st.session_state.assessment_submitted = False
                        st.session_state.current_assessment_topic = assessment_topic
                        st.rerun()
                    else:
                        st.error("Could not generate questions. Please try a different topic or check your course materials.")

else:
    st.info("👆 Please upload your course materials to get started with Lyra!")
    
    # Show features when no files uploaded
    st.markdown("---")
    st.subheader("✨ What Lyra Can Do For You")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🎯 Personalized Learning**
        - Adapts to your learning pace
        - Tracks your progress automatically
        - Identifies knowledge gaps
        
        **💬 24/7 Q&A Support**
        - Ask questions anytime
        - Get detailed, clear answers
        - Interactive dialogue for deeper understanding
        """)
    
    with col2:
        st.markdown("""
        **📝 Exam Preparation**
        - Personalized practice questions
        - Instant feedback on answers
        - Track improvement over time
        
        **📊 Progress Tracking**
        - See your learning journey
        - Monitor topic mastery
        - Get personalized recommendations
        """)

# Footer
st.markdown("---")
st.markdown("*Lyra - Empowering students to learn faster and more effectively* 🚀")