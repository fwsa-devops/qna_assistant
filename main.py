import streamlit as st
from assistant import fetch_question, grade_answer, create_thread

# Streamlit UI layout
st.title("AI-Powered Grading System")

# Initialize session state
if "question" not in st.session_state:
    st.session_state.question = None
    st.session_state.question_id = 1
    st.session_state.answer = None
    st.session_state.feedback = None
    st.session_state.topic = None
    st.session_state.thread = create_thread()  # Create a thread for this session

# Step 1: Input Topic for Question Generation
topic = st.text_input(
    "Enter a Topic:", 
    help="The topic from which the question must be generated",
    value=st.session_state.topic if st.session_state.topic else ""
)

# Step 2: Fetch or display generated question
if topic != st.session_state.topic:
    st.session_state.topic = topic
    st.session_state.question = None  # Trigger new question generation
    st.session_state.question_id = 1
    st.session_state.answer = None
    st.session_state.feedback = None
    st.session_state.thread = create_thread()  # Create a new thread for the new topic

if topic:
    if st.session_state.question is None:
        # Fetch the question based on the topic
        _question = fetch_question(topic, st.session_state.thread.id)
        st.session_state.question = _question.question
        st.session_state.question_id = _question.id

    st.write(f"**Question:** {st.session_state.question_id}")
    st.write(f"{st.session_state.question.in_english}")
    st.write(f"{st.session_state.question.in_tamil}")

    # Step 3: Text area for user to answer the question
    answer = st.text_area("Your Answer:", value=st.session_state.answer if st.session_state.answer else "")

    # Step 4: Button to submit and display grading
    if st.button("Submit Answer"):
        if answer:
            score, feedback = grade_answer(answer, st.session_state.thread.id)
            st.session_state.correctness_score = score
            st.session_state.feedback = feedback

            st.write(f"**Correctness Score:** {st.session_state.correctness_score}")
            st.write(f"**Feedback:** ")
            st.write(f"{st.session_state.feedback['in_english']}")
            st.write(f"{st.session_state.feedback['in_tamil']}")

            # Buttons to either try another question or input a new topic
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Try Another Question"):
                    st.session_state.question = None  # Trigger new question generation
                    st.session_state.answer = None
                    st.session_state.feedback = None
            with col2:
                if st.button("Enter New Topic"):
                    st.session_state.topic = None  # Reset topic to allow input of a new topic
                    st.session_state.question = None
                    st.session_state.answer = None
                    st.session_state.feedback = None
                    st.session_state.thread = create_thread()  # Create a new thread for a new topic
        else:
            st.write("Please enter an answer before submitting.")
else:
    st.write("Please enter a topic to generate a question.")