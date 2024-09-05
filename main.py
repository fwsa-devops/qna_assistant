import streamlit as st
from assistant import fetch_question, grade_answer, create_thread


# Streamlit UI layout
st.title("AI-Powered Grading System")


thread = create_thread()
# Step 1: Input Topic for Question Generation
topic = st.text_input(
    "Enter a Topic:", help="The topic from which the question must be generated"
)


# Step 2: Display generated question (placeholder for now, replace with API call)
if topic:
    
    if "question" not in st.session_state:
        st.session_state.question = None
        st.session_state.question_id = 1
        st.session_state.answer = None
        st.session_state.feedback = None

    # Fetch or display generated question
    if st.session_state.question is None:
        # Placeholder for API call to generate the question based on the topic
        _question = fetch_question(topic, thread.id)
        st.session_state.question = _question.question

    st.write(
        f"**Question {st.session_state.question_id}:** {st.session_state.question}"
    )

    # Step 3: Text area for user to answer the question
    answer = st.text_area("Your Answer:")

    # Step 4: Button to submit and display grading
    if st.button("Submit Answer"):
        if answer:

            grader_response = grade_answer(answer, thread.id)
            print(grader_response)

            # Placeholder for API call to grade the answer
            # Simulated grading response
            correctness_score = str(grade_answer["correctness_score"])
            feedback = grade_answer["feedback"]

            st.write(f"**Correctness Score:** {correctness_score}")
            st.write(f"**Feedback:** {feedback}")

            # Reset for next question
            st.session_state.question_id += 1
            st.session_state.question = None  # To trigger new question generation
        else:
            st.write("Please enter an answer before submitting.")
