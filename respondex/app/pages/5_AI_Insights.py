"""
Page 5: AI Insights — RAG Chatbot v2
Natural language queries with follow-ups, retry, and conversation memory.
"""

import streamlit as st
from utils.styles import inject_dashboard_css
from utils.ai_insights import ask_question

st.set_page_config(page_title="AI Insights | Respondex", layout="wide", page_icon="📊")
inject_dashboard_css()

st.title("AI Insights")
st.caption("Ask questions about Boston 311 data in natural language")

st.markdown("""
<div style="
    background: linear-gradient(135deg, rgba(59,130,246,0.05) 0%, rgba(99,102,241,0.03) 100%);
    border: 1px solid rgba(59,130,246,0.12);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 1.5rem;
    font-size: 0.88rem;
    color: #64748B;
    line-height: 1.6;
">
    Ask a question and Respondex will query the database, analyze the results, and generate a narrative.
    Follow-up questions use conversation context. Powered by <strong style="color:#E2E8F0">Gemini 2.5 Flash</strong>.
</div>
""", unsafe_allow_html=True)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# --- Starter Questions (shown only when no messages) ---
if not st.session_state.messages:
    st.markdown("##### Start with a question")
    starters = [
        "What are the top 10 incident types by volume?",
        "Which neighborhoods have the worst SLA compliance?",
        "How does weekend performance compare to weekdays?",
        "What month has the highest 311 volume?",
    ]
    cols = st.columns(2)
    for i, q in enumerate(starters):
        with cols[i % 2]:
            if st.button(q, key=f"starter_{i}", use_container_width=True):
                st.session_state.pending_question = q
                st.rerun()

# --- Display Chat History ---
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant":
            # Data table
            if msg.get("data") is not None and not msg["data"].empty:
                st.dataframe(msg["data"], use_container_width=True, hide_index=True)

            # SQL citation
            if msg.get("sql"):
                with st.expander("📎 View SQL query", expanded=False):
                    st.code(msg["sql"], language="sql")

            # Follow-up suggestions
            if msg.get("follow_ups"):
                st.markdown("---")
                st.markdown(
                    "<span style='font-size:0.78rem; color:#64748B; letter-spacing:0.05em; text-transform:uppercase;'>"
                    "Follow-up questions</span>",
                    unsafe_allow_html=True,
                )
                for fi, fq in enumerate(msg["follow_ups"]):
                    if st.button(fq, key=f"followup_{idx}_{fi}", use_container_width=True):
                        st.session_state.pending_question = fq
                        st.rerun()

# --- Handle Input ---
question = st.chat_input("Ask a question about Boston 311 data...")

# Check for pending question (from starter or follow-up button)
if st.session_state.pending_question:
    question = st.session_state.pending_question
    st.session_state.pending_question = None

if question:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            result = ask_question(question, st.session_state.messages)

        if result["error"]:
            st.error(result["error"])
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠ {result['error']}",
            })
        else:
            # Narrative
            st.markdown(result["narrative"])

            # Data table
            if result["data"] is not None and not result["data"].empty:
                st.dataframe(result["data"], use_container_width=True, hide_index=True)

            # SQL citation
            if result["sql"]:
                with st.expander("📎 View SQL query", expanded=False):
                    st.code(result["sql"], language="sql")

            # Follow-up suggestions
            if result["follow_ups"]:
                st.markdown("---")
                st.markdown(
                    "<span style='font-size:0.78rem; color:#64748B; letter-spacing:0.05em; text-transform:uppercase;'>"
                    "Follow-up questions</span>",
                    unsafe_allow_html=True,
                )
                for fi, fq in enumerate(result["follow_ups"]):
                    if st.button(fq, key=f"new_followup_{fi}", use_container_width=True):
                        st.session_state.pending_question = fq
                        st.rerun()

            # Save to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["narrative"],
                "data": result["data"],
                "sql": result["sql"],
                "follow_ups": result.get("follow_ups", []),
            })

# --- Clear Chat ---
if st.session_state.messages:
    st.sidebar.divider()
    if st.sidebar.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
