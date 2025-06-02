# legal_ui.py: Streamlit UI for LexTrek

import streamlit as st
import requests
import re
import csv
from datetime import datetime
import time

st.set_page_config(page_title="LexTrek Legal Assistant", layout="wide")

st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }
    .stTextArea textarea {
        font-size: 16px;
    }
    .result-box {
        background-color: #fdfdfd;
        border-left: 6px solid #2b8cd1;
        padding: 1.2em;
        margin-top: 1em;
        border-radius: 0.6em;
        box-shadow: 1px 1px 4px rgba(0,0,0,0.05);
        font-size: 1rem;
        line-height: 1.6;
    }
    .citation-box {
        background-color: #e4f0fb;
        padding: 0.6em 1em;
        border-radius: 0.5em;
        margin-top: 1em;
        font-size: 0.9rem;
        text-align: left;
    }
    .landing-box {
        background: linear-gradient(135deg, #ebf5fc 0%, #ffffff 100%);
        padding: 2em;
        border-radius: 1em;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        margin-bottom: 2em;
    }
    .landing-box h1 {
        color: #2b8cd1;
        font-size: 2.2rem;
    }
    .landing-box p {
        font-size: 1.05rem;
        color: #333;
        margin-top: 0.5em;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="landing-box">
    <h1>🔍 LexTrek – Swiss Legal Assistant</h1>
    <p>Ask a legal question, and LexTrek will respond with a structured summary based on case law and statutes.</p>
</div>
""", unsafe_allow_html=True)

# --- Input Area ---
question = st.text_area("📘 Your Legal Question", height=90)

# --- Ask Button ---
if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a legal question.")
    else:
        start_time = time.time()
        with st.spinner("💬 Consulting LexTrek, please wait..."):
            try:
                res = requests.post(
                    "https://295e-2a02-aa12-3340-c700-a8c9-d0c3-7b87-88d2.ngrok-free.app/query",
                    json={"question": question},
                    timeout=60
                )
                res.raise_for_status()
                answer = res.json().get("answer", "No answer returned.")

                # Clean numbering from answer (e.g., 1. 2. etc.)
                clean_answer = re.sub(r"(?m)^\d+\.\s+", "", answer)

                # --- Display Answer ---
                st.markdown("### 🧾 Answer")
                st.markdown(f"<div class='result-box'>{clean_answer}</div>", unsafe_allow_html=True)

                # --- Extract Unique Citations ---
                citations = re.findall(r"(BGE \d{3} [IVX]+ \d+|Art\. \d+ [A-Z]+)", answer)
                unique_citations = sorted(set(citations))
                if unique_citations:
                    st.markdown("### 📌 Citations Found")
                    st.markdown("<div class='citation-box'>" + ", ".join(f"<code>{c}</code>" for c in unique_citations) + "</div>", unsafe_allow_html=True)

                # --- Response Time ---
                elapsed_time = round(time.time() - start_time, 2)
                st.markdown(f"**⏱️ Response Time:** {elapsed_time} seconds")

                # --- Log Query ---
                with open("query_log.csv", "a") as f:
                    writer = csv.writer(f)
                    writer.writerow([datetime.now(), question, answer])

            except Exception as e:
                st.error(f"❌ Failed to reach LexTrek API:\n{e}")
