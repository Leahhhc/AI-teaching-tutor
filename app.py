import os
import tempfile
from typing import List

import streamlit as st
import pandas as pd

from main import LearningAssistant

# import inspect
# from parsers.lecture_parser import LectureParser
# from memory.storage import Storage


# ---------- Helpers ----------

def get_assistant() -> LearningAssistant:
    """Get or create a LearningAssistant bound to the current user."""
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = "demo_user"

    if "assistant" not in st.session_state:
        st.session_state["assistant"] = LearningAssistant(
            user_id=st.session_state["user_id"]
        )

    if st.session_state.get("user_id") != st.session_state.get("assistant_user_id"):
        st.session_state["assistant"] = LearningAssistant(
            user_id=st.session_state["user_id"]
        )
        st.session_state["assistant_user_id"] = st.session_state["user_id"]

    return st.session_state["assistant"]


def init_state():
    """Initialize UI-related session state."""
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "current_course" not in st.session_state:
        st.session_state["current_course"] = None
    if "current_quiz" not in st.session_state:
        st.session_state["current_quiz"] = None
    if "last_quiz_result" not in st.session_state:
        st.session_state["last_quiz_result"] = None


# ---------- Streamlit Layout ----------

st.set_page_config(
    page_title="AI Teaching Tutor",
    layout="wide",
)

st.title("🧑‍🏫 AI Teaching Tutor")
st.caption(
    "Interactive teaching assistant with adaptive quizzes, progress tracking, "
    "and course-aware explanations."
)

init_state()
assistant = get_assistant()

# ---------- Sidebar: user id & course upload ----------

with st.sidebar:
    st.header("👤 User & Course")

    user_id = st.text_input("User ID", value=st.session_state["user_id"])
    if user_id != st.session_state["user_id"]:
        st.session_state["user_id"] = user_id
        assistant = get_assistant()

    # st.caption(f"DEBUG LectureParser file: {inspect.getfile(LectureParser)}")
    # st.caption(f"DEBUG Storage file: {inspect.getfile(Storage)}")

    st.markdown("---")

    uploaded = st.file_uploader("Upload course PDF", type=["pdf"])
    if uploaded is not None:
        if st.button("📚 Process & Index Course"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name

            with st.spinner("Parsing PDF and building vector index..."):
                result = assistant.upload_course(tmp_path)

            try:
                os.remove(tmp_path)
            except OSError:
                pass

            if result.get("success"):
                st.session_state["current_course"] = result["course"]
                st.success(f"Loaded course: {result['course']['title']}")
            else:
                st.error(f"Upload failed: {result.get('message', 'Unknown error')}")

    if st.session_state["current_course"] is not None:
        course = st.session_state["current_course"]
        st.success(f"Current course: **{course['title']}**")
    else:
        st.info("No course loaded yet. The tutor can still answer questions, "
                "but will be more powerful with a PDF uploaded.")

    st.markdown("---")
    st.caption("Tip: change User ID to simulate different students.")


# ---------- Main Tabs ----------

tab_chat, tab_quiz, tab_progress, tab_next = st.tabs(
    ["💬 Tutor Chat", "📝 Quiz", "📊 Progress", "🎯 Next Step"]
)

# ====== 1. Tutor Chat Tab ======

with tab_chat:
    st.subheader("💬 Tutor Chat")

    mode = st.radio(
        "Mode",
        ["Ask a question", "Explain a concept"],
        horizontal=True,
    )

    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])

    user_msg = st.chat_input(
        "Type your question or concept here…",
        key="chat_input",
    )

    if user_msg:
        st.session_state["chat_history"].append(
            {"role": "user", "content": user_msg}
        )
        with st.chat_message("user"):
            st.markdown(user_msg)

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                if mode == "Ask a question":
                    result = assistant.ask_question(user_msg)
                    if result.get("success"):
                        answer = result["answer"]
                    else:
                        answer = f"Error: {result.get('message', 'Unknown error')}"
                else:
                    result = assistant.explain_concept(user_msg)
                    if result.get("success"):
                        answer = result["explanation"]
                    else:
                        answer = f"Error: {result.get('message', 'Unknown error')}"

                st.markdown(answer)

        st.session_state["chat_history"].append(
            {"role": "assistant", "content": answer}
        )

# ====== 2. Quiz Tab ======

with tab_quiz:
    st.subheader("📝 Adaptive Quiz")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        topic = st.text_input(
            "Topic / keyword for quiz",
            placeholder="e.g., open set recognition, overfitting, backpropagation…",
        )
        num_questions = st.slider("Number of questions", 3, 10, 5, step=1)

        if st.button("Generate Quiz"):
            if not topic.strip():
                st.warning("Please enter a topic first.")
            else:
                with st.spinner("Generating quiz…"):
                    result = assistant.generate_quiz(
                        topic=topic,
                        num_questions=num_questions,
                    )

                if result.get("success"):
                    st.session_state["current_quiz"] = result["quiz"]
                    st.session_state["last_quiz_result"] = None
                    st.success(
                        f"Generated quiz on '{topic}' "
                        f"(difficulty {result['difficulty']}/5)."
                    )
                else:
                    st.error(f"Quiz generation failed: {result.get('message')}")

    with col_right:
        if st.session_state["current_quiz"] is not None:
            quiz = st.session_state["current_quiz"]
            st.markdown("**Current Quiz Info**")
            st.write(f"Topic: `{quiz['topic']}`")
            st.write(f"Questions: {len(quiz['questions'])}")
        else:
            st.info("No quiz generated yet.")

    st.markdown("---")

    quiz = st.session_state["current_quiz"]
    if quiz is not None:
        st.markdown("### Questions")

        for idx, q in enumerate(quiz["questions"]):
            st.markdown(f"**Q{idx + 1}. {q['question']}**")

            option_keys = list(q["options"].keys())

            def _fmt(opt_key: str) -> str:
                return f"{opt_key}. {q['options'][opt_key]}"

            selected = st.radio(
                "Your answer:",
                option_keys,
                format_func=_fmt,
                key=f"quiz_q_{idx}",
                index=None,
            )
            st.write("")

        if st.button("Submit Quiz"):
            answers: List[str] = []
            missing = False

            for idx, q in enumerate(quiz["questions"]):
                value = st.session_state.get(f"quiz_q_{idx}")
                if value is None:
                    missing = True
                answers.append(value)

            if missing:
                st.warning("Please answer all questions before submitting.")
            else:
                with st.spinner("Evaluating quiz…"):
                    result = assistant.submit_quiz(user_answers=answers)

                if result.get("success"):
                    st.session_state["last_quiz_result"] = result
                    score = result["score"]
                    st.success(
                        f"Score: {score * 100:.1f}%  "
                        f"({result['correct']}/{result['total']} correct)"
                    )

                    st.markdown("#### Detailed Feedback")
                    for d in result["details"]:
                        q_idx = d["question_num"] - 1
                        q_data = quiz["questions"][q_idx]
                        correct_letter = d["correct_answer"]
                        is_correct = d["is_correct"]

                        if is_correct:
                            st.markdown(f"✅ **Q{d['question_num']}** correct")
                        else:
                            st.markdown(f"❌ **Q{d['question_num']}** incorrect")

                        st.markdown(f"- Your answer: `{d['user_answer']}`")
                        st.markdown(f"- Correct answer: `{correct_letter}`")
                        st.markdown(
                            f"- Explanation: {q_data.get('explanation', 'N/A')}"
                        )
                        st.write("")
                else:
                    st.error(f"Submit failed: {result.get('message')}")

    else:
        st.info("Generate a quiz to start answering questions.")


# ====== 3. Progress Tab ======

with tab_progress:
    st.subheader("📊 Learning Progress")

    result = assistant.get_progress()

    if not result.get("success"):
        st.error(result.get("message", "Failed to fetch progress."))
    else:
        overall = result.get("overall_mastery", 0.0)
        topics = result.get("topics", {})

        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Overall mastery", f"{overall * 100:.1f}%")

        with col2:
            if topics:
                df = pd.DataFrame(
                    [
                        {"topic": t, "mastery": m}
                        for t, m in topics.items()
                    ]
                )
                df = df.sort_values("mastery", ascending=False)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No topics yet. Take at least one quiz to see progress.")

        st.markdown("---")

        if topics:
            st.markdown("### Learning Curve")
            topic_for_curve = st.selectbox(
                "Select a topic",
                options=list(topics.keys()),
            )
            if st.button("Show learning curve"):
                curve_result = assistant.get_learning_curve(topic_for_curve)
                if curve_result.get("success"):
                    curve = curve_result["curve"]
                    if curve:
                        ts = [c[0] for c in curve]
                        vals = [c[1] for c in curve]
                        curve_df = pd.DataFrame(
                            {"timestamp": ts, "mastery": vals}
                        ).set_index("timestamp")
                        st.line_chart(curve_df)
                    else:
                        st.info("No history yet for this topic.")
                else:
                    st.error(curve_result.get("message", "Failed to get curve."))


# ====== 4. Next Step Tab ======

with tab_next:
    st.subheader("🎯 Next Recommended Step")

    if st.button("Get Recommendation"):
        with st.spinner("Computing next best action…"):
            result = assistant.next_recommendation()

        if result.get("success"):
            s = result["suggestion"]
            st.success("Here is your personalized recommendation:")
            st.markdown(f"- **Topic:** `{s['next_topic_id']}`")
            st.markdown(f"- **Suggested difficulty:** `{s['difficulty']}`")
            st.markdown(f"- **Action type:** `{s['action_type']}`")

            st.info(
                "You can paste the topic back into the *Quiz* tab or ask the tutor "
                "to explain it in the *Chat* tab."
            )
        else:
            st.error(result.get("message", "Failed to get recommendation."))
    else:
        st.info("Click the button to see what you should learn next.")
